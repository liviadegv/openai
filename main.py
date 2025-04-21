import asyncio
import speech_recognition as sr
from openai import AsyncOpenAI
from elevenlabs import play
from elevenlabs.client import ElevenLabs

eleven_client = ElevenLabs(api_key="")

openai_client = AsyncOpenAI(api_key="")
assistant_id = ""  

def falar(texto: str):
    audio = eleven_client.text_to_speech.convert(
        text=texto,
        voice_id="",
        model_id="",
        output_format="",
    )
    play(audio)

def ouvir():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga algo...")
        audio = r.listen(source, timeout=6)
        
        try:
            texto = r.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {texto}")
            return texto
        except sr.UnknownValueError:
            print("Não entendi o que você disse")
            return None
        except sr.RequestError:
            print("Erro ao se conectar ao serviço de reconhecimento de fala")
            return None

async def responder_openai(thread_id: str, mensagem: str):
    """ Envia a mensagem ao Assistant e obtém a resposta. """
    await openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=mensagem
    )

    run = await openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(1)
        run = await openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    messages = await openai_client.beta.threads.messages.list(thread_id=thread_id)
    resposta_gerada = messages.data[0].content[0].text.value
    print(f"Assistant: {resposta_gerada}")
    return resposta_gerada

async def main():
    thread = await openai_client.beta.threads.create()
    thread_id = thread.id

    while True:
        print("\nEsperando sua resposta em áudio...")
        mensagem_usuario = ouvir()

        if mensagem_usuario is None:
            continue

        if "tchau" in mensagem_usuario.lower():
            print("Tchau! Até mais!")
            falar("Tchau! Até mais!")
            break

        resposta_gerada = await responder_openai(thread_id, mensagem_usuario)
        falar(resposta_gerada)

        await asyncio.sleep(1)

asyncio.run(main())
