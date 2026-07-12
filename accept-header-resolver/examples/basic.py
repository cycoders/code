from accept_header_resolver import resolve
print(resolve('text/html,application/json;q=0.9', ['application/json', 'text/html']))