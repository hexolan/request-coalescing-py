# Request Coalescing in Async Python

## About

This repository is a simple experiment revolved around implementing request coalescing in Python using Asyncio and FastAPI, inspired by the Discord Engineering team's blog post on [How Discord Stores Trillions of Messages.](https://discord.com/blog/how-discord-stores-trillions-of-messages)

## How does it work?

When a client makes a request for an item, as they're name in this demo, of a specific id, it adds a task to the coalescer queue and waits for the result of that task. Any subsequent requests for items of the same ID, in the meantime, will subscribe to the future result of that first pending task instead of performing their own read query.

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

The number of database queries has fallen from 1:1 with requests to 1 database call per 5 requests (lining up with there being 5 requests being made concurrently in the tests).

## License and Contributing

Please feel free to make pull requests containing any suggestions for improvements.

This repository is open sourced under the [MIT License.](/LICENSE)