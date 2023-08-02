from transformers import BartTokenizer, BartForConditionalGeneration

class TextSummarizer:

    def __init__(self):
        self.model_name = 'facebook/bart-large-cnn'
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)

    def summarize(self, text, max_length=130, min_length=30):
        inputs = self.tokenizer([text], max_length=1024, return_tensors='pt')
        # num_beams for beam search which is a search algorithm used for finding the most likely sequence of words
        summary_ids = self.model.generate(inputs['input_ids'], num_beams=4, max_length=max_length, min_length=min_length, length_penalty=2.0)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
        return summary


if __name__ == "__main__":
    summarizer = TextSummarizer()
    text = """This is a long paragraph that needs to be summarized. It contains many details that might not be important for a summary. Microsoft Corporation is an American multinational technology company that develops, manufactures, licenses, supports, and sells computer software, consumer electronics, personal computers, and related services. Founded by Bill Gates and Paul Allen on April 4, 1975, Microsoft rose to dominate the personal computer operating system market with MS-DOS in the mid-1980s, followed by the Microsoft Windows line of operating systems. The company's flagship products include the Windows operating systems, the Microsoft Office suite, and the Azure cloud computing platform.
    Over the years, Microsoft has expanded its product portfolio through acquisitions, including the purchase of Skype Technologies, LinkedIn, and GitHub. It has also ventured into hardware with products like the Xbox gaming console, Surface tablets, and the Microsoft HoloLens mixed reality headset. In addition, the company offers online services such as Bing search engine, Outlook.com email service, and the Microsoft Azure cloud platform.
    Microsoft has had a significant impact on the technology industry, shaping the way people use computers and software. Its operating systems have become the standard for personal computers worldwide, and its Office suite is widely used for productivity tasks. The company's software and services have enabled businesses and individuals to enhance their productivity, collaborate effectively, and access information and entertainment.
    In recent years, Microsoft has been focusing on artificial intelligence (AI) and cloud computing. Its Azure cloud platform has gained popularity among businesses for its scalability, reliability, and comprehensive set of services. Microsoft's AI initiatives include the development of conversational AI agents, machine learning tools, and AI-powered applications across various domains.
    With a market capitalization exceeding $2 trillion, Microsoft is one of the world's most valuable companies. It employs over 160,000 people globally and operates in multiple countries. The company is known for its philanthropic efforts, with initiatives like the Microsoft Philanthropies, which aims to use technology for social good and bridge the digital divide.
    Microsoft is a prominent technology company known for its operating systems, software products, cloud services, and hardware devices. With a strong focus on AI and cloud computing, the company continues to innovate and shape the technology industry."""
    print(summarizer.summarize(text))