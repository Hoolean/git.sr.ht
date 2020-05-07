package model

import (
	"encoding/json"
	"fmt"
	"io"

	"git.sr.ht/~sircmpwn/git.sr.ht/api/crypto"
)

// TODO: Add a field for the resource this is intended to be used with
type Cursor struct {
	Count   int    `json:"count"`
	Next    string `json:"next"`
	OrderBy string `json:"order_by"`
	Search  string `json:"search"`
}

func (cur *Cursor) UnmarshalGQL(v interface{}) error {
	enc, ok := v.(string)
	if !ok {
		return fmt.Errorf("cursor must be strings")
	}
	plain := crypto.Decrypt([]byte(enc))
	if plain == nil {
		return fmt.Errorf("Invalid cursor")
	}
	err := json.Unmarshal(plain, cur)
	if err != nil {
		// This is guaranteed to be a programming error
		panic(err)
	}
	return nil
}

func (cur Cursor) MarshalGQL(w io.Writer) {
	data, err := json.Marshal(cur)
	if err != nil {
		panic(err)
	}
	w.Write([]byte("\""))
	w.Write(crypto.Encrypt(data))
	w.Write([]byte("\""))
}

func derefOrInt(i *int, d int) int {
	if i != nil {
		return *i
	}
	return d
}

func NewCursor(filter *Filter) *Cursor {
	if filter != nil {
		return &Cursor{
			Next: "",

			Count: derefOrInt(filter.Count, 25),
			// TODO:
			OrderBy: "",
			Search:  "",
		}
	}
	return &Cursor{
		Count:   25,
		Next:    "",
		OrderBy: "",
		Search:  "",
	}
}
