FROM python

WORKDIR D:/PyCharm Edu/study/comp7940 project/

COPY chatbot_zyy.py .
COPY requirements.txt .
COPY config.ini .

RUN pip install pip update
RUN pip install -r requirements.txt

ENV OPENAI=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
ENV YOUTUBE=AIzaSyAFUulNZXNEXG3FGYqKMSO5dpQRd8SL_5w
ENV TRANSKEY=7d8ed46035mshdcda18c3691622cp1c031ejsn3635c03c334d
ENV TRANSHOST=google-translator8.p.rapidapi.com
ENV TRANSURL=https://google-translator8.p.rapidapi.com/translate
ENV DBURL=mongodb+srv://zyy0328:zyy98328@cluster0.9f4tolb.mongodb.net/?retryWrites=true&w=majority

CMD ["python", "chatbot_zyy.py"]