//go:build generate
// +build generate

package loaders

//go:generate ./gen RepositoriesByIDLoader int api/graph/model.Repository
//go:generate ./gen RepositoriesByOwnerRepoNameLoader [2]string api/graph/model.Repository
//go:generate ./gen UsersByIDLoader int api/graph/model.User
//go:generate ./gen UsersByNameLoader string api/graph/model.User
