from discord import app_commands
from discord.ext import commands
import discord, json, os

class configCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    configGroup = app_commands.Group(name="config", description=f"Configuração do Suporte", guild_only=True)

    @configGroup.command(description="Liste os canais que o bot irá responder voluntariamente")
    async def listar_canais(self, interaction: discord.Interaction):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        texto = ""
        for _id in dados["channels"]:
            texto += f"\n<#{_id}>"

        if texto == "":
            await interaction.response.send_message("Nenhum canal configurado.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Segue abaixo os canais configurados: {texto}", ephemeral=True)

    @configGroup.command(description="Comando para adicionar canais que o bot irá responder voluntariamente.")
    async def adicionar_canal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        if canal.id in dados["channels"]:
            await interaction.response.send_message("Esse canal já está na lista de canais.", ephemeral=True)
            return

        dados["channels"].append(canal.id)

        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message(f"Canal {canal.mention} adicionado à lista de canais!", ephemeral=True)

    @configGroup.command(description="Comando para remover canais que o bot irá responder voluntariamente.")
    async def remover_canal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        if canal.id not in dados["channels"]:
            await interaction.response.send_message("Esse canal não está na lista de canais.", ephemeral=True)
            return

        dados["channels"].remove(canal.id)

        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message(f"Canal {canal.mention} removido da lista de canais!", ephemeral=True)

    @configGroup.command(description="Selecione o canal que o bot sempre irá responder.")
    async def setar_canal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)
        
        if dados["channel_onlybot"] == canal.id:
            await interaction.response.send_message("A configuração atual já é este canal.", ephemeral=True)
            return
    
        dados["channel_onlybot"] = canal.id

        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message(f"Canal {canal.mention} setado com sucesso!", ephemeral=True)


    @configGroup.command(description="Sete o prompt para a IA.")
    async def setar_prompt(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ModalSetPrompt(self.client))

    @configGroup.command(description="Adicione uma pergunta para o 'FAQ'.")
    async def adicionar_pergunta(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ModalNewQuestionForFAQ(self.client))

    @configGroup.command(description="Remova uma pergunta do FAQ")
    async def remover_pergunta(self, interaction: discord.Interaction, pergunta: str):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        existe = False
        nova_lista = []
        for faq in dados["faq"]:
            if faq['pergunta'] == pergunta:
                existe = True
            else:
                nova_lista.append(faq)

        if not existe:
            await interaction.response.send_message("Essa pergunta não existe.", ephemeral=True)
            return
        
        dados["faq"] = nova_lista

        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message(f"`{pergunta}` removida com sucesso!", ephemeral=True)

    @configGroup.command(description="Liste as perguntas que o bot tem cadastrado no FAQ.")
    async def listar_perguntas(self, interaction: discord.Interaction):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        texto = ""
        for faq in dados["faq"]:
            texto += f"\nPergunta: {faq['pergunta']} / Resposta: {faq['resposta']}"

        if texto == "":
            await interaction.response.send_message("Nenhuma pergunta configurada.", ephemeral=True)
        else:
            if len(texto) > 1800:
                with open("./message.txt", 'w') as arquivo:
                    arquivo.write(texto)
                await interaction.response.send_message("Segue as perguntas configuradas: ", ephemeral=True, file=discord.File("./message.txt"))
                os.remove("./message.txt")
                return
            await interaction.response.send_message(f"Segue as perguntas configuradas: {texto}", ephemeral=True)

    @configGroup.command()
    async def clear(self, interaction: discord.Interaction):
        await interaction.channel.purge(limit=1000)

class ModalSetPrompt(discord.ui.Modal):
    def __init__(self, client):
        super().__init__(title="Setando o prompt")
        self.client = client
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)
            
        self.prompt = discord.ui.TextInput(style=discord.TextStyle.paragraph, label="Informe o prompt do bot", required=True)
        self.prompt.default = dados["prompt"]
        self.add_item(self.prompt)

    async def on_submit(self, interaction: discord.Interaction):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)
        
        dados["prompt"] =  self.prompt.value
        
        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message("Prompt alterado com sucesso!", ephemeral=True)

class ModalNewQuestionForFAQ(discord.ui.Modal):
    def __init__(self, client):
        super().__init__(title="Adicionando pergunta")
        self.client = client
        self.pergunta = discord.ui.TextInput(style=discord.TextStyle.short, label="Pergunta", required=True)
        self.resposta = discord.ui.TextInput(style=discord.TextStyle.short, label="Resposta", required=True)
        self.add_item(self.pergunta)
        self.add_item(self.resposta)

    async def on_submit(self, interaction: discord.Interaction):
        with open('./data.json', 'r') as arquivo:
            dados = json.load(arquivo)

        for question in dados["faq"]:
            if question["pergunta"] == self.pergunta.value:
                await interaction.response.send_message("Essa pergunta já existe!", ephemeral=True)
                return
        
        dados["faq"].append(
            {
                "pergunta":self.pergunta.value, 
                "resposta":self.resposta.value
            }
        )

        with open('./data.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=4)

        await interaction.response.send_message("Pergunta adicionada com sucesso!", ephemeral=True)

async def setup(client):
    await client.add_cog(configCommands(client))
    