package main

import (
	"context"

	"git.sr.ht/~sircmpwn/core-go/config"
	"git.sr.ht/~sircmpwn/core-go/server"
	"git.sr.ht/~sircmpwn/core-go/webhooks"
	work "git.sr.ht/~sircmpwn/dowork"
	"github.com/99designs/gqlgen/graphql"

	"git.sr.ht/~sircmpwn/git.sr.ht/api/graph"
	"git.sr.ht/~sircmpwn/git.sr.ht/api/graph/api"
	"git.sr.ht/~sircmpwn/git.sr.ht/api/graph/model"
	"git.sr.ht/~sircmpwn/git.sr.ht/api/loaders"
	"git.sr.ht/~sircmpwn/git.sr.ht/api/repos"
)

func main() {
	appConfig := config.LoadConfig(":5101")

	gqlConfig := api.Config{Resolvers: &graph.Resolver{}}
	gqlConfig.Directives.Access = func(ctx context.Context, obj interface{},
		next graphql.Resolver, scope model.AccessScope,
		kind model.AccessKind) (interface{}, error) {
		return server.Access(ctx, obj, next, scope.String(), kind.String())
	}
	schema := api.NewExecutableSchema(gqlConfig)

	scopes := make([]string, len(model.AllAccessScope))
	for i, s := range model.AllAccessScope {
		scopes[i] = s.String()
	}

	reposQueue := work.NewQueue("repos")
	webhookQueue := webhooks.NewQueue(schema)
	legacyWebhooks := webhooks.NewLegacyQueue()

	server.NewServer("git.sr.ht", appConfig).
		WithDefaultMiddleware().
		WithMiddleware(
			loaders.Middleware,
			repos.Middleware(reposQueue),
			webhooks.Middleware(webhookQueue),
			webhooks.LegacyMiddleware(legacyWebhooks),
		).
		WithSchema(schema, scopes).
		WithQueues(reposQueue, webhookQueue.Queue, legacyWebhooks.Queue).
		Run()
}
