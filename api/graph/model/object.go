package model

import (
	"errors"
	"fmt"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing"
	"github.com/go-git/go-git/v5/plumbing/object"
)

type Object interface {
	IsObject()
}

func LookupObject(repo *git.Repository, hash plumbing.Hash) (Object, error) {
	obj, err := repo.Object(plumbing.AnyObject, hash)
	if err != nil {
		return nil, fmt.Errorf("lookup object %s: %w", hash.String(), err)
	}
	// TODO: Add raw object data, if requested
	switch obj := obj.(type) {
	case *object.Commit:
		return CommitFromObject(repo, obj), nil
	case *object.Tree:
		return TreeFromObject(repo, obj), nil
	case *object.Blob:
		return BlobFromObject(repo, obj), nil
	default:
		return nil, errors.New("Unknown object type")
	}
}
