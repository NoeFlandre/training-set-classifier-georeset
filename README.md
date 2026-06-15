# training-set-classifier-georeset

In this repository we are building a training set for a classifier to filter sentences based on their relevance to environment/ agriculture. The data for this project will be stored in this bucket: "https://huggingface.co/buckets/NoeFlandre/training-set-classifier-georeset"

We are proceeding as follows:

- We are starting with a set of tags which are relevant to environment and agriculture. These tags were selected from a prior study. 
- Given these tags we are selecting OpenStreetMap polygons which are satisfying these tags and are distributed across the Earth in a more or less balanced fashion (we want them to be geographically spread across continents and distant from each other). 
- Polygons should have non empty names and a tag from the selected list of tags. THey will be sorted also based on their area. A polygon belongs to one of the following bin : {tiny <0.1, small 0.1-1, medium 1-10, large >=10} where a number is in km^2. Polygons should be deduplicated (e.g based on osm_type and osm_id). Polygons should be stratified across area bins and world regions (e.g continents)
- Based on these polygons we are building internet queries, in English only first, the internet query does contain the polygon name, the location of this polygon along with a term which is going to specify some theme of interest (e.g biodiversity).
- For the internet query, we are going to use BRAVE API in the first place. Result per query should be set to 20 and rate limits should be respected with a search delay of 1.2 seconds. 
- We are going to make sure our pipeline is resumable and logged
- We will be extracting text from HTML using trafilatura. 
- Once the text is extracted we will be giving it a score based on duplicate sentences, whether lines are short, lines empty or not and so on. 
- A sentence is going to be kept if it is including between 8 to 80 words, has a terminal punctuation and does not terminate by an ellipsis (e.g "..."), has a symbol to word ratio small enough. 
- Using MinHash we will make sure to duplicate sentences. 
- Based on these extracted sentences we will be using an LLM to label them as relevant or not for our use case. 
- A human reviewer will be manually labelling an held out set in order to compute an inter rater agreement between the LLM and the human judge for us to understand whether the LLM agrees with what we would expect a human to output for our use case.
