resource "google_project_iam_member" "storage_object_admin" {
  for_each = toset(var.team_members)

  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = each.value
}

resource "google_project_iam_member" "viewer" {
  for_each = toset(var.team_members)

  project = var.project_id
  role    = "roles/viewer"
  member  = each.value
}
