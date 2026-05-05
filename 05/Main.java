public class Main {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("musisz podać witryny jako argumenty uruchomienia programu.");
            return;
        }

        HttpClientService client = new HttpClientService();

        for (String domain : args) {
            System.out.println("Witryna: " + domain);
            
            String serverHttp = client.getServer("http://" + domain);
            System.out.println("[HTTP] (80) Server: " + serverHttp);

            String serverHttps = client.getServer("https://" + domain);
            System.out.println("[HTTPS] (443) Server: " + serverHttps);

            String htmlHttp = client.getHTML("http://" + domain);
            System.out.println("[HTTP] (80) HTML: " + htmlHttp);

            String htmlHttps = client.getHTML("https://" + domain);
            System.out.println("[HTTPS] (443) HTML: " + htmlHttps);
        }
    }
}