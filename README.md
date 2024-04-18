# Request Coalescing in Async Python

A simple experiment revolved around implementing request coalescing in Python, using Asyncio and FastAPI, inspired by the Discord Engineering team's blog post on [How Discord Stores Trillions of Messages.](https://discord.com/blog/how-discord-stores-trillions-of-messages)

## How does it work?

When a client makes a request for an item of a specific id, it will add a task to the coalescer queue and await the result of that task.

Any subsequent requests recieved in the meantime, for items of the same id, will subscribe to the future result of that first pending task instead of performing their own expensive read query.

![Coalescing Diagram](/docs/img-1.png)

## Testing

```bash
> poetry run pytest
tests\test_standard.py Making 5x100 concurrent requests (500 total)...
Standard Requests: Took 457.228ms
Standard Metrics: {'requests': 500, 'db_calls': 500}

tests\test_coalesced.py Making 5x100 concurrent requests (500 total)...
Coalesced Requests: Took 49.328ms
Coalesced Metrics: {'requests': 500, 'db_calls': 100}
```

The number of database queries has fallen from 1:1 with requests to 1 database call per 5 requests (when coalescing and performing 5 requests concurrently).

## License and Contributing

Please feel free to open an issue or a pull request to discuss suggestions for improvements.

This repository is open source under the [MIT License.](/LICENSE)
