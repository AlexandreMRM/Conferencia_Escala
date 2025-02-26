FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-dev \
    libglib2.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libpangocairo-1.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && apt-get clean

# Instale pacotes de localidade e o locale-gen
RUN apt-get update && apt-get install -y locales

# Gera a localidade 'pt_BR.UTF-8'
RUN sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# Definir as variáveis de ambiente para o locale
ENV LANG pt_BR.UTF-8  
ENV LANGUAGE pt_BR:pt  
ENV LC_ALL pt_BR.UTF-8  

WORKDIR /app

COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o conteúdo do diretório local para o contêiner
COPY . .

EXPOSE 8088

CMD ["streamlit", "run", "app.py", "--server.port=8088", "--server.enableCORS=false"]
