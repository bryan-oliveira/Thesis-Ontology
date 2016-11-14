import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class ThesisScraperV2 {
	
	private static int thesisScraped = 0;
	
	public static void main(String[] args) throws IOException {
		
		Document master1 = Jsoup.connect("https://estudogeral.sib.uc.pt/handle/10316/104/collhome?type=title").get();
		Document master2 = Jsoup.connect("https://estudogeral.sib.uc.pt/handle/10316/104/collhome?type=title&order=ASC&offset=20").get();
		
		Document phd1 = Jsoup.connect("https://estudogeral.sib.uc.pt/handle/10316/103/collhome?type=title").get();
		
		Document [] masterThesisDocs = {master1,master2};
		Document [] phdThesisDocs = {phd1};
		
		ThesisScraper(masterThesisDocs, "Master Thesis");
		ThesisScraper(phdThesisDocs, "Doctoral Thesis");
		
		System.out.println("Thesis's scraped: " + thesisScraped);
	}
	
	public static void ThesisScraper(Document [] list, String thesisType) throws IOException {
		
		PrintWriter pw = new PrintWriter(new FileWriter("thesis.txt"));
		
		for (Document thesisdoc : list) {

			// Fetch Thesis list table
			Elements thesisTable = thesisdoc.select("table.miscTable");
			
			// Select each row
			for (Element tableRow : thesisTable.select("tr")) {
				
				// Get data from each row
				Elements tableData = tableRow.select("td");
				
				// Only rows with more than 3 fields are thesis's
				if(tableData.size() > 3) {

					String title = " ";
					String author = " ";
					String advisor = ""; // Empty on purpose
					String year = " ";					
					String keywords = " ";
//					String citation = " "; // Not used yet
					String abstract_ = " ";
					String uri = " ";
//					String fileUri = " "; // Not used yet
					String type = thesisType;
					
					// Get first hyper-link (Thesis Uri)
					Element getUri = tableData.select("a").first();
					uri = getUri.absUrl("href");

					Document newThesisUri = Jsoup.connect(uri).get();
					Elements newThesis = newThesisUri.select(".itemDisplayTable").select("tr");					
					
					for (Element fieldHtml : newThesis) {
						
						// Unencapsulates field; <td class="abc">Title:&nbsp;</td> --> Title:&nbsp;
						Elements field = fieldHtml.children();
						
						for (Element text : field) {
						
							if(text.html().contains("Title")) {
								title = text.nextElementSibling().text();
								//System.out.println("Title - " + title);
							}
							
							if(text.html().contains("Author")) {
								String tmp = text.nextElementSibling().text();
								
								Elements authorLink = fieldHtml.select("a");
								String link = authorLink.attr("abs:href");
								
								int pos = tmp.indexOf(" ");
								int pos2 = tmp.indexOf(",");
								
								author = tmp.substring(pos+1) + " " + tmp.substring(0, pos2) + "[" + link + "]";
								
								//System.out.println("Author - " + author);
							}
							
							if(text.html().contains("Advisor")) {
								Elements advisorList = text.nextElementSibling().select("a");
								
								for (Element element : advisorList) {
									//System.out.println("### - " + element.toString() );
									String tmp = element.text();
									String advisorlink = element.attr("abs:href");
									int pos = tmp.indexOf(" ");
									int pos2 = tmp.indexOf(",");
									advisor += tmp.substring(pos+1) + " " + tmp.substring(0, pos2) + "[" + advisorlink + "]" + ";";
								}
								//System.out.println("Advisor - " + advisor);
							}

							if(text.html().contains("Keywords")) {
								String tmp = text.nextElementSibling().html();
								keywords = tmp.replaceAll("<br>", ";");
								//System.out.println("Keywords - " + keywords);
							}
							
							if(text.html().contains("Issue")) {
								year = text.nextElementSibling().text();
								//System.out.println("Year - " + year);
							}
							
							if(text.text().contains("Abstract")) {
								abstract_ = text.nextElementSibling().text();
								//System.out.println("Abstract - " + abstract_);
							}
							
							if(text.text().contains("URI")) {
								uri = text.nextElementSibling().text();
								//System.out.println("Uri - " + uri);
							}
						}
					}
					
					thesisScraped++;
					String thesisStr = 	 "Title - " 	  + title 	  + "\n" 
										+"Author - " 	  + author    + "\n"
										+"Advisor - " 	  + advisor   + "\n" 
										+"Keywords - " 	  + keywords  + "\n" 
										+"Date - " 		  + year 	  + "\n" 
										+"Abstract - " 	  + abstract_ + "\n" 
										+"Thesis Type - " + type 	  + "\n" 
										+"URI - " 		  + uri 	  + "\n";
					
					System.out.println(thesisStr);
					pw.write(thesisStr);
				}
			}
		}
		pw.close();
	}
}
