Hello Raman,

Cale and I have been working on integrating our parsing code (more technical, not user-friendly) with our website to demonstrate usability. We are building the overall structure for the product and not focusing on the finer details of web-design/polish. The visuals for the website can be upgraded later as focusing on the functionality behind-the-scenes will make future modifications easier. We have attached a video that demonstrates the complete process of user search -> company form retrieval -> company form processing -> financial data storage -> user visualization. 

# Video 1 Notes

- Website is connected to EDGAR database parser
- Searching for a company that has not been processed calls the EDGAR parser for that company
	- **The first lookup for a company is slow, but after being processed once and stored in our database, the retrieval times are on the order of 1 ms**.
	- The user will not be exposed to this slowdown as we will preprocess financial data. The initial slow load will be observed only by us.
- All company data is stored in a friendly format for our future tooling to work with.
- All company data is displayed within a table on the website with the ability to toggle the plotting of each row.
	- Plotting has a normalization toggle which scales the data. Useful for comparing the trends of fields with a large difference in value.

## Work behind-the-scenes

- We have been setting up the website and database that will store company financial data and allow the user to easily interact/retrieve data
- We are setting up a framework for handling future features within our system while still being flexible. 
- API documentation is formalized and uses a standard tool (Swagger)
	- This means that if we decide to sell access to our API as an additional product, it is compatible with tools that are commonly used in application development.
- We can add additional features if you have ideas
	- Examples we have
		- Default equations for each company (NAV, EPV, GV, ...)
			- User has the option to view what financial statement fields/information is being used to calculate the data
			- User can copy the model equation and modify it to their own needs
		- Selling access to our financial data API
		- Additional pages like "Raman's Investment Corner"
			- Could be blog-like and have some occasional in-depth analysis for a company
				- Free portion has a broad overview of the analysis
				- Paid portion has in-depth analysis
