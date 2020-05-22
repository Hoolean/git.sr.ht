package graph

import (
	gqlmodel "git.sr.ht/~sircmpwn/gql.sr.ht/model"

	"git.sr.ht/~sircmpwn/git.sr.ht/api/graph/api"
)

func cursorComplexity(c int, cursor *gqlmodel.Cursor) int {
	if cursor != nil {
		return c * cursor.Count
	}
	return c
}

func ApplyComplexity(conf *api.Config) {
	conf.Complexity.Query.Repositories = func(c int, cursor *gqlmodel.Cursor, filter *gqlmodel.Filter) int {
		c = cursorComplexity(c, cursor)
		if filter != nil && filter.Count != nil {
			c *= *filter.Count
		}
		return c
	}
	conf.Complexity.Repository.AccessControlList = func(c int, cursor *gqlmodel.Cursor) int {
		return cursorComplexity(c, cursor)
	}
	conf.Complexity.Repository.Log = func(c int, cursor *gqlmodel.Cursor, from *string) int {
		return cursorComplexity(c, cursor)
	}
	conf.Complexity.Repository.Objects = func(c int, ids []string) int {
		return c * len(ids)
	}
	conf.Complexity.Repository.References = func(c int, cursor *gqlmodel.Cursor) int {
		return cursorComplexity(c, cursor)
	}
	conf.Complexity.Tree.Entries = func(c int, cursor *gqlmodel.Cursor) int {
		return cursorComplexity(c, cursor)
	}
	conf.Complexity.User.Repositories = func(c int, cursor *gqlmodel.Cursor, filter *gqlmodel.Filter) int {
		c = cursorComplexity(c, cursor)
		if filter != nil && filter.Count != nil {
			c *= *filter.Count
		}
		return c
	}
}
