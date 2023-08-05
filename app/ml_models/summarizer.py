from transformers import BartTokenizer, BartForConditionalGeneration

class TextSummarizer:

    def __init__(self):
        self.model_name = 'facebook/bart-large-cnn'
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)

    def summarize(self, text, max_length=1024, min_length=30):

        inputs = self.tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)

        # num_beams for beam search which is a search algorithm used for finding the most likely sequence of words
        summary_ids = self.model.generate(inputs['input_ids'], num_beams=4, max_length=max_length, min_length=min_length, length_penalty=2.0)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
        return summary


if __name__ == "__main__":
    summarizer = TextSummarizer()
    text = """
    China's economy will maintain stable and positive growth in the second half of this year, following a sustained recovery in the first half as a raft of policies have begun to take effect, China's top economic planner said at a press conference Friday.\n\nYuan Da, director of the Department of National Economy at the 
    National Development of Reform Commission (NDRC), highlighted positive changes in various economic indicators for July, such as faster growth in power generation, improving market expectations and a two-month rise in the manufacturing purchasing managers' index.
    """
    print(summarizer.summarize(text))