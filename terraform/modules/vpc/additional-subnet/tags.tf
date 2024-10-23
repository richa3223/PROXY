locals {
  contacts = format("%s%s",
    length(var.developer_dl) == 0 ?
    format("%s", "")
    :
    format("%s", var.developer_dl),
    length(var.tech_ops) == 0 ?
    format("%s", "")
    :
    format("+%s", var.tech_ops)
  )
  global_tag = {
    TaggingVersion = var.tag_version
    contacts       = local.contacts
  }

  global_tags = merge(var.global_tags, local.global_tag)
}
