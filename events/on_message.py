from discord.ext import commands
import json
from g4f.client import Client


class on_msg(commands.Cog):
    def __init__(self, client): 
        self.client = client
        self.assistant_client = Client()
		
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        with open("./data.json", 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        if message.channel.id in dados["channels"]:
            try:
                prompt = f'Irei te fornecer uma lista de perguntas e respostas. Verifique se a mensagem "{message.content}" é uma PERGUNTA parecida (faz sentido) com as perguntas informadas, atenção: sua resposta só deve ser SIM se a mensagem for uma pergunta. Responda somente "SIM" ou "NÃO". Alguns termos pouco comuns que são similares: Allowlist é o mesmo que AL, WL, Whitelist, Cidade é o mesmo que Server, Servidor, City. Segue a lista de perguntas:'
                for question in dados['faq']:
                    prompt += f"\nPergunta {question['pergunta']} | Resposta: {question['resposta']}"

                chat_history = [
                    {"role": "system", "content": prompt}
                ]

                r1 = self.assistant_client.chat.completions.create(
                    model="gpt-4o",
                    messages=chat_history,
                )

                if r1.choices[0].message.content == "SIM":
                    prompt = f"{dados['prompt']}"
                    for question in dados['faq']:
                        prompt += f"\nPergunta {question['pergunta']} | Resposta: {question['resposta']}"

                    chat_history = [
                        {"role": "system", "content": prompt}
                    ]

                    chat_history.append({"role":"user", "content":message.content})

                    response = self.assistant_client.chat.completions.create(
                        model="gpt-4o",
                        messages=chat_history,
                    )
                    
                    await message.reply(response.choices[0].message.content)
            except RuntimeWarning:
                pass
            except UserWarning:
                pass

        elif message.channel.id == dados["channel_onlybot"]:
            prompt = f"{dados['prompt']}"
            for question in dados['faq']:
                prompt += f"\nPergunta {question['pergunta']} | Resposta: {question['resposta']}"
            chat_history = [
                {"role": "system", "content": prompt}
            ]

            chat_history.append({"role":"user", "content":message.content})

            response = self.assistant_client.chat.completions.create(
                model="gpt-4o",
                messages=chat_history,
            )
            await message.reply(response.choices[0].message.content)


async def setup(client):
    await client.add_cog(on_msg(client))
    