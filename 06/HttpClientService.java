import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Optional;

public class HttpClientService {
    private final HttpClient httpClient;
    private final String url;

    public HttpClientService(String url) {
        this.url = url;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String getHTML() throws IOException, InterruptedException {
        HttpRequest request = createRequest();
        HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return processResponse(response);
    }

    private HttpRequest createRequest() {
        return HttpRequest.newBuilder()
                .uri(URI.create(this.url))
                .GET()
                .build();
    }

    private String processResponse(HttpResponse<String> response) throws IOException {
        if (response.statusCode() != 200) {
            throw new IOException("Serwer zwrócił kod błędu: " + response.statusCode());
        }
        
        if (!isContentTypeHtml(response)) {
            String type = response.headers().firstValue("Content-Type").orElse("nieznany");
            throw new IOException("Oczekiwano dokumentu HTML, ale otrzymano typ: " + type);
        }
        
        return response.body();
    }

    private boolean isContentTypeHtml(HttpResponse<String> response) {
        Optional<String> contentType = response.headers().firstValue("Content-Type");
        return contentType.isPresent() && contentType.get().toLowerCase().contains("text/html");
    }
}