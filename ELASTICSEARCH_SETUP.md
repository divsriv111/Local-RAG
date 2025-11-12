# Elasticsearch Configuration for RAG Chatbot Logs

## Index Lifecycle Management (ILM) Setup

This guide shows how to configure automatic log retention and cleanup in Elasticsearch.

---

## 1. Create ILM Policy (30-Day Retention)

```bash
curl -X PUT "localhost:9200/_ilm/policy/rag-chatbot-logs-policy?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "1d",
            "max_primary_shard_size": "50gb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "set_priority": {
            "priority": 50
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'
```

### Policy Explanation:
- **Hot Phase (0-7 days)**: Active logs, high priority, rollover daily or at 50GB
- **Warm Phase (7-30 days)**: Older logs, optimized for storage
- **Delete Phase (30+ days)**: Automatically delete old logs

---

## 2. Create Index Template

```bash
curl -X PUT "localhost:9200/_index_template/rag-chatbot-logs-template?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "index_patterns": ["rag-chatbot-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "index.lifecycle.name": "rag-chatbot-logs-policy",
      "index.lifecycle.rollover_alias": "rag-chatbot-logs",
      "index.refresh_interval": "30s",
      "index.mapping.total_fields.limit": 2000
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "Level": {
          "type": "keyword"
        },
        "MessageTemplate": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "Message": {
          "type": "text"
        },
        "CorrelationId": {
          "type": "keyword"
        },
        "UserId": {
          "type": "keyword"
        },
        "WorkspaceId": {
          "type": "keyword"
        },
        "ChatHistoryId": {
          "type": "keyword"
        },
        "MachineName": {
          "type": "keyword"
        },
        "EnvironmentName": {
          "type": "keyword"
        },
        "ThreadId": {
          "type": "integer"
        },
        "Application": {
          "type": "keyword"
        },
        "RequestPath": {
          "type": "keyword"
        },
        "RequestMethod": {
          "type": "keyword"
        },
        "StatusCode": {
          "type": "integer"
        },
        "Elapsed": {
          "type": "float"
        },
        "RemoteIpAddress": {
          "type": "ip"
        },
        "UserAgent": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "Exception": {
          "type": "text"
        },
        "StackTrace": {
          "type": "text"
        },
        "FileName": {
          "type": "keyword"
        },
        "FileSize": {
          "type": "long"
        },
        "Duration": {
          "type": "float"
        },
        "Model": {
          "type": "keyword"
        },
        "QueryLength": {
          "type": "integer"
        },
        "ResponseLength": {
          "type": "integer"
        },
        "ResponseTime": {
          "type": "float"
        }
      }
    }
  },
  "priority": 200,
  "composed_of": [],
  "version": 1,
  "_meta": {
    "description": "Template for RAG Chatbot application logs"
  }
}'
```

---

## 3. Verify Configuration

### Check ILM Policy
```bash
curl -X GET "localhost:9200/_ilm/policy/rag-chatbot-logs-policy?pretty"
```

### Check Index Template
```bash
curl -X GET "localhost:9200/_index_template/rag-chatbot-logs-template?pretty"
```

### Check Indices
```bash
curl -X GET "localhost:9200/_cat/indices/rag-chatbot-logs-*?v&s=index"
```

### Check ILM Status for Indices
```bash
curl -X GET "localhost:9200/rag-chatbot-logs-*/_ilm/explain?pretty"
```

---

## 4. Manual Operations

### Force Rollover (for testing)
```bash
curl -X POST "localhost:9200/rag-chatbot-logs/_rollover?pretty"
```

### Delete Old Indices Manually
```bash
# Delete indices older than 30 days
curl -X DELETE "localhost:9200/rag-chatbot-logs-2024.*?pretty"
```

### Reindex to Apply New Mapping
```bash
curl -X POST "localhost:9200/_reindex?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "source": {
    "index": "rag-chatbot-logs-old-*"
  },
  "dest": {
    "index": "rag-chatbot-logs-new"
  }
}'
```

---

## 5. Monitoring

### View ILM Policies
```bash
curl -X GET "localhost:9200/_ilm/policy?pretty"
```

### View Index Lifecycle
```bash
curl -X GET "localhost:9200/rag-chatbot-logs-*/_settings?pretty" | grep lifecycle
```

### Check Disk Usage
```bash
curl -X GET "localhost:9200/_cat/allocation?v"
```

### Monitor ILM Errors
```bash
curl -X GET "localhost:9200/_ilm/status?pretty"
```

---

## 6. Kibana Setup

### Create Index Pattern
1. Go to **Stack Management** → **Index Patterns**
2. Click **Create index pattern**
3. Index pattern: `rag-chatbot-logs-*`
4. Time field: `@timestamp`
5. Click **Create index pattern**

### Create Visualizations

#### 1. Error Rate Over Time
```json
{
  "type": "line",
  "query": {
    "match": {
      "Level": "Error"
    }
  },
  "aggregation": {
    "date_histogram": {
      "field": "@timestamp",
      "interval": "1h"
    }
  }
}
```

#### 2. Authentication Failures
```json
{
  "type": "pie",
  "query": {
    "match": {
      "MessageTemplate": "Authentication failed*"
    }
  },
  "aggregation": {
    "terms": {
      "field": "Username.keyword"
    }
  }
}
```

#### 3. Average LLM Response Time
```json
{
  "type": "metric",
  "query": {
    "exists": {
      "field": "ResponseTime"
    }
  },
  "aggregation": {
    "avg": {
      "field": "ResponseTime"
    }
  }
}
```

#### 4. PDF Upload Statistics
```json
{
  "type": "data_table",
  "query": {
    "match": {
      "MessageTemplate": "PDF upload completed*"
    }
  },
  "aggregation": {
    "terms": {
      "field": "WorkspaceId.keyword"
    },
    "sub_aggregations": {
      "total_size": {
        "sum": {
          "field": "FileSize"
        }
      },
      "avg_duration": {
        "avg": {
          "field": "Duration"
        }
      }
    }
  }
}
```

---

## 7. Alerts (Using Elasticsearch Watcher)

### Alert on High Error Rate
```bash
curl -X PUT "localhost:9200/_watcher/watch/high-error-rate?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["rag-chatbot-logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "match": {
                    "Level": "Error"
                  }
                },
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-5m"
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": {
        "gt": 10
      }
    }
  },
  "actions": {
    "log_error": {
      "logging": {
        "text": "High error rate detected: {{ctx.payload.hits.total.value}} errors in last 5 minutes"
      }
    }
  }
}'
```

### Alert on Failed Authentications
```bash
curl -X PUT "localhost:9200/_watcher/watch/failed-auth-attempts?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "trigger": {
    "schedule": {
      "interval": "1m"
    }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["rag-chatbot-logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "match": {
                    "MessageTemplate": "Authentication failed*"
                  }
                },
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-5m"
                    }
                  }
                }
              ]
            }
          },
          "aggs": {
            "by_username": {
              "terms": {
                "field": "Username.keyword"
              }
            }
          }
        }
      }
    }
  },
  "condition": {
    "script": {
      "source": "return ctx.payload.aggregations.by_username.buckets.stream().anyMatch(bucket -> bucket.doc_count > 5);"
    }
  },
  "actions": {
    "log_warning": {
      "logging": {
        "text": "Multiple failed authentication attempts detected"
      }
    }
  }
}'
```

---

## 8. Performance Tuning

### Increase Heap Size (for large log volumes)
```yaml
# In elasticsearch.yml or docker-compose.yml
ES_JAVA_OPTS: "-Xms2g -Xmx2g"
```

### Optimize Refresh Interval
```bash
curl -X PUT "localhost:9200/rag-chatbot-logs-*/_settings?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "index": {
    "refresh_interval": "30s"
  }
}'
```

### Force Merge Old Indices
```bash
curl -X POST "localhost:9200/rag-chatbot-logs-2024.10.*/_forcemerge?max_num_segments=1&pretty"
```

---

## 9. Backup and Restore

### Create Snapshot Repository
```bash
curl -X PUT "localhost:9200/_snapshot/rag_logs_backup?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "type": "fs",
  "settings": {
    "location": "/backups/elasticsearch",
    "compress": true
  }
}'
```

### Create Snapshot
```bash
curl -X PUT "localhost:9200/_snapshot/rag_logs_backup/snapshot_1?wait_for_completion=true&pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "indices": "rag-chatbot-logs-*",
  "ignore_unavailable": true,
  "include_global_state": false
}'
```

### Restore Snapshot
```bash
curl -X POST "localhost:9200/_snapshot/rag_logs_backup/snapshot_1/_restore?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
  "indices": "rag-chatbot-logs-*",
  "ignore_unavailable": true,
  "include_global_state": false
}'
```

---

## 10. Troubleshooting

### Logs Not Appearing
1. Check Elasticsearch is running: `curl http://localhost:9200`
2. Check API logs: `./logs/elasticsearch-failures-*.txt`
3. Verify Elasticsearch URI in `appsettings.json`
4. Check network connectivity between API and Elasticsearch

### High Disk Usage
1. Check index sizes: `curl "localhost:9200/_cat/indices?v&s=store.size:desc"`
2. Manually delete old indices
3. Adjust ILM retention policy
4. Increase disk space or move to separate volume

### Slow Query Performance
1. Check shard count: `curl "localhost:9200/_cat/shards?v"`
2. Optimize field mappings (use `keyword` instead of `text` where appropriate)
3. Add more nodes to cluster
4. Use index patterns in queries to limit scope

### ILM Not Working
1. Check ILM status: `curl "localhost:9200/_ilm/status?pretty"`
2. View ILM explain: `curl "localhost:9200/rag-chatbot-logs-*/_ilm/explain?pretty"`
3. Restart ILM: `curl -X POST "localhost:9200/_ilm/start?pretty"`

---

## Quick Reference Commands

```bash
# View all indices
GET /_cat/indices/rag-chatbot-logs-*?v

# Count documents
GET /rag-chatbot-logs-*/_count

# Search recent logs
GET /rag-chatbot-logs-*/_search
{
  "size": 20,
  "sort": [{"@timestamp": "desc"}],
  "query": {"match_all": {}}
}

# Search errors
GET /rag-chatbot-logs-*/_search
{
  "query": {
    "match": {"Level": "Error"}
  }
}

# Search by correlation ID
GET /rag-chatbot-logs-*/_search
{
  "query": {
    "match": {"CorrelationId": "YOUR-GUID-HERE"}
  }
}

# Delete index
DELETE /rag-chatbot-logs-2024.10.01

# Check cluster health
GET /_cluster/health?pretty

# View node stats
GET /_nodes/stats?pretty
```

---

## Production Checklist

- [ ] ILM policy configured (30-day retention)
- [ ] Index template created with proper mappings
- [ ] Kibana index pattern created
- [ ] Basic visualizations and dashboards set up
- [ ] Alerts configured for critical errors
- [ ] Backup repository configured
- [ ] First snapshot created
- [ ] Elasticsearch authentication enabled
- [ ] TLS/SSL configured for production
- [ ] Firewall rules configured
- [ ] Log retention policy documented
- [ ] Team trained on Kibana usage
- [ ] Monitoring and alerting tested

---

For production deployment, consider using Elastic Cloud or a managed Elasticsearch service for automatic scaling, backups, and updates.
