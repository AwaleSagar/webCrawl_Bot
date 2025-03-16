### **Overview**

The project involves building a keyword-based web crawler. This application will allow users to input keywords and then automatically explore the internet, starting from a given set of web addresses. The crawler will visit web pages, follow the links it finds, and analyze the content of each page to identify if it's relevant to the user's keywords. If a page is relevant, its title and web address will be stored. The crawler will also respect website rules about crawling. The final result will be a list of relevant web pages found during the crawl. This project will be developed in stages, starting with basic functionality and gradually adding more advanced features and the ability to scale.

### **Phase 1: Establishing the Core Functionality (Single Machine)**

1. **Set Up the Development Environment:**  
   * Install Python 3.x, ensuring it's added to the system's PATH environment variable.  
   * Install the necessary Python libraries: requests, beautifulsoup4, and nltk using pip. It is recommended to install these within a virtual environment.  
   * (Optional) Download NLTK data packages if you plan to use stemming, lemmatization, or stop word removal. This can be done using nltk.download() in a Python interpreter.  
2. **Implement the User Command-Line Interface:**  
   * Use Python's input() function to allow users to enter keywords.  
   * Instruct users to separate multiple keywords with spaces or commas.  
   * Process the input string using methods like split() to get individual keywords.  
   * Handle potential leading or trailing whitespace using the strip() method.  
   * (Alternative) Consider using command-line arguments via the sys module for more advanced interaction.  
3. **Develop the Keyword Processing Module:**  
   * **Tokenization:** Split the input keywords into individual words or tokens. Use the word\_tokenize() function from the nltk library for more complex scenarios.  
   * **Normalization:** Convert all keywords to lowercase using the .lower() method to ensure case-insensitive matching.  
   * **(Optional) Stemming/Lemmatization:** Reduce words to their root form using stemmers (like PorterStemmer from nltk) or lemmatizers (like WordNetLemmatizer from nltk) to account for different word inflections.  
   * **(Optional) Stop Word Removal:** Remove common words (like "the", "a", "is") using the list of stop words provided by nltk.corpus.stopwords.  
4. **Define and Manage Seed URLs:**  
   * Create a list of initial URLs (seed URLs) that will serve as the starting point for the crawler. These should be relevant to the keywords users are likely to search for.  
   * Initialize the crawler with this list of seed URLs.  
5. **Build the Basic Web Crawling Algorithm:**  
   * **Initialize Data Structures:** Create a queue (e.g., using collections.deque in Python) to hold URLs to be crawled and a set to keep track of visited URLs. Add the seed URLs to the queue.  
   * **Crawling Loop:** Start a loop that continues as long as the queue is not empty.  
   * **Dequeue URL:** In each iteration, remove a URL from the front of the queue.  
   * **Check if Visited:** Before crawling, check if the URL is already in the visited set. If yes, skip it.  
   * **Mark as Visited:** If not visited, add the URL to the visited set.  
   * **Fetch HTML Content:** Use the requests.get() method to retrieve the HTML content of the web page. Handle potential errors like network issues or HTTP error responses.  
   * **Basic Robots.txt Compliance:** Before fetching content, check the website's /robots.txt file to see if crawling is disallowed, especially for the root path / for all user agents \*.  
   * **Parse HTML and Extract Text:** Use the beautifulsoup4 library to parse the HTML content. Extract visible text from relevant HTML tags (e.g., \<p\>, \<h1\> to \<h6\>, \<li\>, \<div\>) using the .get\_text() method.  
   * **Content Matching:** Search for the processed user keywords within the extracted text using simple string searching techniques. Define criteria for determining relevance (e.g., all keywords must be present).  
   * **Extract Page Title:** Locate the \<title\> tags within the \<head\> section of the HTML and retrieve the page title using beautifulsoup4 methods like soup.title.string or soup.find('title').get\_text().  
   * **Extract Links:** Find all \<a\> tags on the page using soup.find\_all('a') and extract the value of the href attribute for each link using link.get('href').  
   * **Filter and Add Links to Queue:** Filter the extracted links based on criteria like staying within the same domain, removing duplicates, and ensuring they are valid URLs. Add the filtered links to the back of the crawling queue.  
   * **Implement Delay:** Use time.sleep() to introduce a delay between consecutive requests to be polite to web servers.  
6. **Implement Temporary Data Storage and Output Mechanisms:**  
   * Use an in-memory data structure (like a list of dictionaries or a dictionary) to store the URLs and titles of relevant pages.  
   * Once the crawl is complete, display the collected page titles and URLs to the user in a readable format on the command line.

### **Phase 2: Enhancements and Refinements for Single Machine Operation**

1. **Incorporate Crawl Depth Control:** Associate a depth level with each URL in the queue. Increment the depth for newly discovered links. Configure a maximum allowed depth and skip crawling URLs that exceed this limit.  
2. **Implement Robust Robots.txt Handling:** Use the urllib.robotparser module in Python to parse and handle robots.txt files more accurately. Use the RobotFileParser class and its can\_fetch(useragent, url) method to check if the crawler is allowed to access specific URLs.  
3. **Enhance Content Matching Techniques:**  
   * **Regular Expressions:** Use Python's re module to perform more sophisticated pattern matching for keywords and their variations.  
   * **TF-IDF (Term Frequency-Inverse Document Frequency):** Implement TF-IDF to score the relevance of web pages to the user's keywords, allowing for ranking of results.  
4. **Implement File System Based Data Persistence:** Save the crawled results (page titles and URLs) to a file in a structured format like CSV or JSON using Python's csv and json modules. Allow users to configure the output file format and location.  
5. **Add Comprehensive Error Handling and Logging:** Use try-except blocks to handle potential exceptions during network requests, HTML parsing, and file operations. Utilize Python's logging module to record events, warnings, and errors to a log file.  
6. **Set a Custom User Agent String:** Configure the crawler to send a custom User-Agent header with HTTP requests to identify the crawler.  
7. **Provide User-Configurable Parameters:** Allow users to configure parameters like seed URLs, crawl depth, delay between requests, output file format, and keyword processing options through command-line arguments, configuration files, or environment variables.

### **Phase 3: Integrating with Database Systems (Single Machine)**

1. **Selecting an Appropriate Database Solution:**
   * Choose SQLite for initial development due to its simplicity and file-based nature.
   * Install the required packages: `sqlite3` is included in Python's standard library, so no additional installation is required.
   * For potential future migration to MySQL/PostgreSQL, outline the database requirements: ability to store URLs, page titles, content snippets, relevance scores, and metadata.
   * Consider the trade-offs: SQLite is simpler but less scalable, while MySQL/PostgreSQL offer better performance for larger datasets but require more setup.

2. **Designing the Database Schema:**
   * Create a `crawled_pages` table with the following columns:
     - `id` (INTEGER): Primary key with auto-increment
     - `url` (TEXT): The URL of the crawled page (with a unique constraint)
     - `title` (TEXT): The title of the page
     - `content_snippet` (TEXT): A short excerpt of the page content (optional)
     - `relevance_score` (REAL): The calculated relevance score (0.0-1.0)
     - `depth` (INTEGER): The crawl depth at which this page was found
     - `crawl_time` (TIMESTAMP): When the page was crawled
     - `keywords_matched` (TEXT): Which keywords were matched in the content
   * Create a `crawl_metadata` table to store information about each crawl session:
     - `id` (INTEGER): Primary key with auto-increment
     - `start_time` (TIMESTAMP): When the crawl started
     - `end_time` (TIMESTAMP): When the crawl ended
     - `keywords` (TEXT): The keywords used for the crawl
     - `pages_crawled` (INTEGER): Total number of pages crawled
     - `relevant_pages_found` (INTEGER): Number of relevant pages found
   * Add appropriate indexes:
     - Index on `url` in the `crawled_pages` table for quick lookups
     - Index on `relevance_score` for efficient sorting/filtering
     - Index on `crawl_time` for time-based queries

3. **Implementing the Database Connection Module:**
   * Create a new file `src/database_manager.py` to handle all database operations.
   * Implement functions for:
     - Initializing the database and creating tables if they don't exist
     - Opening and closing database connections
     - Inserting new crawled pages
     - Querying for existing pages
     - Updating page data if recrawled
     - Retrieving crawl results based on various criteria
   * Use connection pooling for efficiency when making multiple database operations.
   * Implement proper error handling and transaction management to ensure data integrity.

4. **Integrating Database Storage with the Crawler:**
   * Modify the `WebCrawler` class to accept a database connection or manager.
   * Update the crawler to store found pages in the database instead of in-memory lists.
   * Implement methods to check if a URL has already been crawled by querying the database.
   * Add functionality to update existing entries if a page is recrawled with new information.
   * Create a crawl session record at the start of each crawl and update it at the end.
   * Ensure proper database connection handling even if the crawler terminates unexpectedly.

5. **Implementing Query Mechanisms and Visualization:**
   * Create functions to query the database for:
     - Most relevant pages for given keywords
     - Recently crawled pages
     - Statistics about crawling sessions
   * Implement a simple command-line interface for querying the crawl results.
   * Add options to export query results to JSON or CSV formats.
   * Create functions to generate basic statistics and metrics about crawled data.

6. **Performance Considerations and Optimization:**
   * Implement batch inserts for better performance when adding multiple pages.
   * Use database transactions to ensure atomicity of related operations.
   * Add configurable options for controlling how much content is stored in the database.
   * Consider implementing data retention policies (e.g., removing old crawl data).
   * Add database vacuuming for SQLite to reclaim space from deleted records.
   * Implement efficient pagination for retrieving large result sets.

7. **Testing and Validation:**
   * Create unit tests for database operations to ensure they work as expected.
   * Test the system with various crawl scenarios and database sizes.
   * Validate data integrity with sample queries.
   * Develop test cases for edge conditions like database locked errors.
   * Measure and optimize performance for larger crawls.

8. **Documentation and Usage Guide:**
   * Document the database schema and relationships between tables.
   * Create example queries for common use cases.
   * Document configuration options for database connections.
   * Provide instructions for backup and recovery procedures.
   * Create migration instructions for moving from file-based storage to database storage.

### **Phase 4: Scaling the Crawler to a Distributed Environment (Cluster Deployment)**

1. **Choosing and Configuring a Distributed Queue System:** Select and set up a distributed message broker (like RabbitMQ or Kafka) or a distributed task queue (like Celery with RabbitMQ or Redis) to manage and distribute URLs to worker nodes.  
2. **Refactoring the Crawling Logic for Worker Processes:** Refactor the core crawling logic into a separate worker process or script that can run on multiple machines. These worker processes will connect to the distributed queue, retrieve URLs, perform crawling tasks, and potentially add new links back to the queue. Design the workers to be stateless.  
3. **Implementing a Central Coordinator Service:** Develop a central coordinator service to manage the overall crawling process. This service can handle user input, initialize the distributed queue, monitor worker progress, manage crawl depth limits, and potentially handle rate limiting across the cluster.  
4. **Setting Up a Distributed Database for Scalability:** Choose and configure a distributed database system to handle the increased volume of data generated by a distributed crawler. Consider options like distributed SQL databases or NoSQL databases. Ensure the worker processes are configured to connect to and store data in this distributed database.  
5. **Implementing Inter-Process Communication and Data Sharing:** Establish mechanisms for communication and data sharing between the central coordinator, worker nodes, and the distributed queue and database systems.  
6. **Monitoring and Management of the Distributed Crawler:** Implement tools and processes for monitoring the health and performance of the distributed crawler, including tracking the number of active workers, queue length, error rates, and overall crawling progress. This includes mechanisms for starting, stopping, and scaling the crawler as needed.