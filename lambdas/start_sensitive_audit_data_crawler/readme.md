# Start sensitive audit data crawler
This lambda starts a crawl of the data inside the sensitive audit event store any time there is a folder created in the bucket.

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose |
|---|---|
| CRAWLER_NAME | The name of the glue data crawler to start|
