import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class HttpClientService {
    private final HttpClient httpClient;

    public HttpClientService() {
        this.httpClient = HttpClient.newHttpClient();
    }

    public String getServer(String url) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET()
                    .build();
            HttpResponse<Void> response = this.httpClient.send(request, HttpResponse.BodyHandlers.discarding());
            return response.headers().firstValue("Server").orElse("Brak nagłówka Server");
        } catch (IOException | InterruptedException | IllegalArgumentException e) {
            return "Błąd: " + e.getMessage();
        }
    }

    public String getHTML(String url) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET()
                    .build();
            HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                return "Błąd: Otrzymano status " + response.statusCode();
            }
            return response.body();
        } catch (IOException | InterruptedException | IllegalArgumentException e) {
            return "Błąd: " + e.getMessage();
        }
    }
}