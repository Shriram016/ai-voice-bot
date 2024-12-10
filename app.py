import assemblyai as aai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from openai import OpenAI

class AI_Assistant:
    
    def __init__(self,):
        aai.settings.api_key="xxxxxxxxxxxxxxxxxxx"
        self.open_ai_client = OpenAI(api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.elevenlabs_api_key = "xxxxxxxxxxxxxxxxxxxxxx"
        
        self.elevenlabs_client  = ElevenLabs(api_key=self.elevenlabs_api_key)
        self.transcriber = None
        
        self.interaction = [{'role':'system',"content":"""You are a helpful travel guide in Himachal Pradesh, India
                             helping a tourist to plan their trip. Be conversational and Precise in your responses."""}]
        
    
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
            
    def start_transcription(self):
        """Starts the microphone to record the audio and transcribe it real time with Assembly AI"""
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=self.on_data, # function when transcript is recevied from Assembly AI
            on_error=self.on_error, # Function when any transcription error Occurs
            on_open= self.on_open, # Function when connection is established with Assembly AI
            on_close = self.on_close, # When closing the current connection
            end_utterance_silence_threshold= 1000
        )
        
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(microphone_stream)
            
    
    def on_open(self,session_opened:aai.RealtimeSessionOpened):
        """This method is evoked when an connection has been established with Assembly AI"""
        print('Session ID:',session_opened.session_id)
        return
    
    def on_error(self,error:aai.RealtimeError):
        """this method is evoked in case of any error with connecting to Assemmbly AI"""
        print('Error:',error)
        return
    
    def on_close(self):
        """This method is evoked while closing a connection"""
        print('Session Closed')
        return
    
    def on_data(self,transcript:aai.RealtimeTranscript):
        """This method is evoked upon receiving a transript from Assembly AI.
        Here we invoke the generate_ai_response function"""
        
        if not transcript.text:
            return
        
        if isinstance(transcript,aai.RealtimeFinalTranscript()):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text,end='\r')
            
        
        
    
    def generate_audio(self,text):
        """This function gets text as input and verbalize the text to speech

        Args:
            text (str): Text that needs to be converted to speech
        """
        self.interaction.append({'role':'assistant',"content":text})
        print(f"AI Guide:{text}")
        
        audio_stream = self.elevenlabs_client.generate(text=text,voice='Rachel',stream=True)
        
        stream(audio_stream)
        
    
    def generate_ai_response(self,transcript):
        """This function accepts the transcribed input, adds it to interaction, and sends to openAI to produce
        a response and finally this response is passd to generate_audio function

        Args:
            transcript (str): _description_
        """
        self.stop_transcription()
        
        self.interaction.append({'role':'user','content':transcript.text})
        
        print(f"Tourist:{ transcript.text}")
        
        # generate response using Open AI
        response = self.open_ai_client.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages=self.interaction,
        )
        
        # Verbalise the response
        
        self.generate_audio(response.choices[0].message.content)
        
        self.start_transcription() # lets the user talk again
        
        print(f"Real time transcription: ")
        
        
        
greeting = "Thank you for calling Himachal Pradesh Travel Guide. My name is Rachel, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()