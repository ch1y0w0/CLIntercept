import requests

def test_proxy(proxy_url, target_url):
    """Test the forward HTTP proxy by sending a request through the proxy."""
    try:
        # Set up the proxy configuration
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        # Send a GET request through the proxy to the target URL
        response = requests.get(target_url, proxies=proxies, timeout=5)

        # Output the result
        print(f"Request to {target_url} through proxy {proxy_url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text[:200]}...")  # Print the first 200 characters for brevity

    except requests.RequestException as e:
        print(f"Error testing proxy: {e}")

if __name__ == "__main__":
    # Proxy server address (assuming it's running on localhost and port 8080)
    proxy_url = "http://localhost:8080"

    # Target URL to test against (httpbin is a public API for testing)
    target_url = "http://httpbin.org/get"

    # Run the test
    test_proxy(proxy_url, target_url)
