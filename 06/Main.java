
import java.io.IOException;

public class Main {
    public static void main(String[] args) {
        HttpClientService client = new HttpClientService("http://th.if.uj.edu.pl");
        String html;

        try {
            html = client.getHTML();
            Main.containsExpectedContent(html, "Institute of Theoretical Physics");
        } catch (IOException | InterruptedException e) {
            System.err.println("Wystąpił błąd podczas pobierania witryny: " + e.getMessage());
            System.exit(1);
        }

    }

    private static void containsExpectedContent(String html, String expectedContent) {
        if (html.contains(expectedContent)) {
            System.out.println("OK - Witryna zawiera podaną frazę: " + expectedContent);
            System.exit(0);
        } else {
            System.out.println("BŁĄD - Witryna nie zawiera podanej frazy: " + expectedContent);
            System.exit(1);
        }
    }
}
