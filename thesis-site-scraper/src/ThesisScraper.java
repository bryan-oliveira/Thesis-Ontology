import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class ThesisScraper {
	
	public static void main(String[] args) throws IOException {
		
		int thesisScraped = 0;
		
		Document page1 = Jsoup.connect("https://estudogeral.sib.uc.pt/handle/10316/104/collhome?type=title").get();
		Document page2 = Jsoup.connect("https://estudogeral.sib.uc.pt/handle/10316/104/collhome?type=title&order=ASC&offset=20").get();
		
		Document [] thesisDocs = {page1,page2};
		
		PrintWriter pw = new PrintWriter(new FileWriter("thesis.txt"));
		
		for (Document thesisdoc : thesisDocs) {

			// Fetch Thesis list table
			Elements thesisTable = thesisdoc.select("table.miscTable");
			
			// Select each row
			for (Element tableRow : thesisTable.select("tr")) {
				
				// Get data from each row
				Elements tableData = tableRow.select("td");
				
				// There is an initial <tr> (row) that doesn't matter so we exclude it outerHtml
				// Rows that interest us have > 3 fields 								
				if(tableData.size() > 3) {
					
					String year = tableData.get(0).text();
					String title = tableData.get(1).text();
					String author = tableData.get(2).text();
					String type = tableData.get(3).text();
					
					String advisor = " ";
					String abstract_ = " ";
					String keywords = " ";
					String temp = null;
					
					// Get first hyper-link (Thesis Uri)
					Element tmp = tableData.select("a").first();
					String uri = tmp.absUrl("href");

					Document newThesis = Jsoup.connect(uri).get();
					Elements elem = newThesis.select(".itemDisplayTable").select("tr");					
					
					for (Element element : elem) {

						if(element.text().contains("Advisor")) {
							temp = element.text();
							int start = temp.indexOf(" ");
							advisor = temp.substring(start);
							//System.out.println(element.text());
						}
						if(element.text().contains("Keywords")) {
							temp = element.text();
							int start = temp.indexOf(" ");
							keywords = temp.substring(start);
							//System.out.println(element.text());
						}
						if(element.text().contains("Abstract")) {
							temp = element.text();
							int start = temp.indexOf(" ");
							abstract_ = temp.substring(start);
							//System.out.println(element.text());
						}
					}
					
					thesisScraped++;

					String thesisStr = year + "|||" + title + "|||" + advisor + "|||" + author + "|||" + keywords + "|||" + abstract_ + "|||" + type + "|||" + uri + "\n";
					System.out.println(thesisStr);
					pw.write(thesisStr);
					
					
				}
			}
		}
		pw.close();
		System.out.println("Thesis's scraped: " + thesisScraped);
	}
}
