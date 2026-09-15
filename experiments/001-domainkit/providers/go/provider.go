// Package provider is a hand-written, ordinary Go library -- the same role
// as providers/py_provider.py, but for the Go target. Nothing here is
// generated; it's exactly what "the developer bootstraps components"
// means. Types come from the mechanically-generated types package so
// there's one canonical definition, not a duplicate per provider.
package provider

import "domainkit/generated/go/types"

func MarkTaskDone(t *types.Task) {
	t.Done = true
}

func SetTaskOwner(t *types.Task, u *types.User) {
	t.Owner = u
}
