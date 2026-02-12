from bs4 import BeautifulSoup 

htmlDoc = """
<html> 
<head>
    <title>Sample Web Page</title>
</head>
<body>
    <h1>Welcome to the Sample Website</h1>
    <div class="content-wrapper">
        <p class="intro-text">This paragraph provides an introduction.</p>
        <a href="https://www.sample.com">Visit Sample.com</a>
    </div>
</body>
</html>
"""

# Initialize BeautifulSoup with the HTML and parser
soup = BeautifulSoup(htmlDoc, 'html.parser')

# Select and print the title element
title = soup.title
print(title.text)  # Output: Sample Web Page

# Find and print the first paragraph with class "intro-text"
paragraph = soup.find('p', class_='intro-text')
print(paragraph.text)  # Output: This paragraph provides an introduction.

# Retrieve and print all links
links = soup.find_all('a')
for link in links:
    print(link.get('href'))  # Output: https://www.sample.com

