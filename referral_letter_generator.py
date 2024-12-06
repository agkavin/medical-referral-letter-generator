import datetime
import os
import re
from langchain.llms import Ollama
from markdown_pdf import MarkdownPdf, Section

class ReferralLetterGenerator:
    def __init__(self, transcript, markdown_template_path, doctor_info="", addressed_to="", contact_info= ""):
        self.transcript = transcript
        self.markdown_template_path = markdown_template_path
        self.doctor_info = doctor_info
        self.addressed_to = addressed_to
        self.contact_info = contact_info
        self.model = Ollama(model="llama3.1")
        self.markdown_content = self.read_markdown_file(self.markdown_template_path)
        
    def read_markdown_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise IOError(f"An error occurred while reading the file: {e}")
    
    def wh_generator(self):
        q_prompt = f"""
        You are an advanced AI tasked with generating precise and comprehensive wh-questions 
        from a given markdown template. The goal is to identify all the key pieces of 
        information needed to fill out the template. Focus on generating questions that 
        explicitly cover every placeholder or section of the template.

        Here is the markdown template:
        ---
        {self.markdown_content}
        ---
        
        Based on this template, create a list of questions that would gather all the 
        necessary information to complete the template accurately. Ensure the questions 
        are well-phrased and cover all relevant sections.
        
        Output the questions in a numbered list format. Dont include any other text other than the questions.
        """
        
        # Generate questions using the model
        response = self.model(q_prompt)
        
        if response:
            return response.strip()
        else:
            raise ValueError("The model did not return a response.")
    
    def answer_extractor(self, questions):
        # Get the current date using datetime
        current_date = datetime.datetime.now().strftime('%d %B, %Y')
        
        # Prompt for the model
        prompt = f"""
        You are an advanced AI tasked with extracting precise answers to a list of questions 
        from a given transcript. Your job is to match the questions with the most relevant 
        information in the transcript and provide concise, accurate answers.

        Here are the questions:
        ---
        {questions}
        ---

        And here is the transcript:
        ---
        {self.transcript}
        ---

        Additionally, here is the doctor's information and the recipient's information:
        Doctor's Info: {self.doctor_info}
        Addressed To: {self.addressed_to}
        Contact Info: {self.contact_info}
        Date: {current_date}

        Extract answers for each question and present them in the following format:
        Question 1: [Question Text]
        Answer: [Answer Text]
        
        Question 2: [Question Text]
        Answer: [Answer Text]

        Continue for all the questions. Ensure the answers are brief, clear, and based solely 
        on the content of the transcript.
        """

        # Generate answers using the model
        response = self.model(prompt)
        
        if response:
            return response.strip()
        else:
            raise ValueError("The model did not return a response.")
    
    def letter_generator(self, answers):
        prompt = f"""
        You are an advanced AI tasked with generating a well-structured, professional referral letter 
        in markdown format by filling out the following template with the provided answers. 

        The referral letter template is as follows:
        ---
        {self.markdown_content}
        ---

        Here are the answers to the questions that should be inserted into the template:
        ---
        {answers}
        ---

        Based on these, generate a complete referral letter in markdown format. 
        Make sure the final letter is grammatically correct, properly structured, 
        and strictly follows the template format.

        Ensure that the letter has proper headings, salutations, and contains all the necessary information. Dont include any other text other than the letter content.
        """

        # Generate the referral letter using the model
        response = self.model(prompt)

        if response:
            return response[response.find("#"):]  
        else:
            raise ValueError("The model did not return a response.")
        
    def verify_markdown_format(self, text):
        # Check for headers (e.g., #, ##, ###)
        if not re.search(r'^\s*#{1,6}\s', text, re.MULTILINE):
            raise ValueError("The generated content is not in proper markdown format.")
        return True
    
    def save_as_markdown(self, text, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f"Content saved to {file_path} successfully.\n")
        except Exception as e:
            raise IOError(f"An error occurred while saving the file: {e}")
    
    def generate_pdf(self, text, pdf_path):
        pdf = MarkdownPdf()
        pdf.meta["title"] = 'Referral Letter'
        pdf.add_section(Section(text, toc=False))
        pdf.save(pdf_path)
        print(f"PDF saved as '{pdf_path}' successfully.")
        
    def generate_referral_letter(self):
        # Step 1: Generate questions from the markdown template
        questions = self.wh_generator()
        
        # Step 2: Extract answers from the transcript
        answers = self.answer_extractor(questions)
        
        # Step 3: Generate the referral letter in markdown format
        letter = self.letter_generator(answers)
        
        # Step 4: Verify markdown format, raise error if invalid
        self.verify_markdown_format(letter)
            
        # Step 5: Save the generated letter
        self.save_as_markdown(letter, 'letter.md')

        # Step 6: Generate PDF from the markdown content
        self.generate_pdf(letter, 'output.pdf')
            
        return letter

