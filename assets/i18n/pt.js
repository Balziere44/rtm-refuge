/* Portugues (BR).

   Scope, decided on purpose and documented in the README: navigation, footer,
   interface labels, the home page and the shared callout headings are
   translated. The long reference text - skill descriptions, levelling spots,
   wiki-derived system pages - stays in English, because those are the exact
   strings people search for and the exact strings the game itself uses. A
   half-translated skill name is worse than an untranslated one.

   Keys are named, never positional. Adding an entry in the middle of a list
   must never change what any other key means. */
window.RTMR_I18N_REGISTER('pt', {

  /* --- navigation -------------------------------------------------------
     Three group labels and five leaves each. The group label has to work as a
     heading in the drawer as well as a button in the row. */
  'nav.home': 'Início',
  'nav.start': 'Comece Aqui',
  'nav.about': 'O Servidor',
  'nav.game': 'O Jogo',
  'nav.reference': 'Referência',
  'nav.join': 'Entrar',

  'nav.server': 'O que é o Refuge',
  'nav.changes': 'O que mudou',
  'nav.faq': 'Perguntas',
  'nav.classes': 'Classes',
  'nav.newjobs': 'Duas novas jobs',
  'nav.mechanics': 'Combate e atributos',
  'nav.gear': 'Equipamentos',
  'nav.world': 'Mundo',
  'nav.database': 'Database',
  'nav.codex': 'Codex',
  'nav.guides': 'Guias',

  /* --- interface -------------------------------------------------------- */
  'a11y.skip': 'Pular para o conteúdo',
  'search.title': 'Buscar no site',
  'search.placeholder': 'Busque classes, habilidades, masmorras, guias...',
  'search.hint': 'Digite para buscar em mais de 500 classes, habilidades, masmorras e seções.',
  'search.none': 'Nada encontrado.',
  'lang.change': 'Mudar idioma',
  'theme.switch': 'Alternar tema',

  'ui.home': 'Início',
  'ui.onThisPage': 'Nesta página',
  'ui.tier': 'Nível',
  'ui.changesFrom': 'Vem de',
  'ui.leadsTo': 'Leva a',
  'ui.weapons': 'Armas',
  'ui.strengths': 'Pontos fortes',
  'ui.weaknesses': 'Pontos fracos',
  'ui.skills': 'Habilidades',
  'ui.whatItIs': 'O que é',
  'ui.refugeChanged': 'O que o Refuge mudou',
  'ui.notInRefuge': 'Não existe no Refuge',
  'ui.newInRefuge': 'Novo no Refuge',
  'ui.filterSkills': 'Filtrar habilidades...',
  'ui.filterDungeons': 'Filtrar por nome, nível ou rank...',

  /* --- calls to action -------------------------------------------------- */
  'cta.join': 'Entrar no servidor da comunidade',
  'cta.start': 'Começar a jogar',
  'cta.howto': 'Como entrar',
  'cta.chat': 'Chat da comunidade',

  /* --- home ------------------------------------------------------------- */
  'home.status': 'Em desenvolvimento &middot; ainda sem data de lançamento',
  'home.h1': 'Os Orphans têm o seu <span class="accent">velho lar</span> de volta.',
  'home.lede': 'Um mundo customizado, reconstruído das cinzas por quem o jogava. ' +
    'Gratuito para jogar, e nunca vai te vender poder.',

  /* --- footer ----------------------------------------------------------- */
  'foot.col0': 'Comece por aqui',
  'foot.col1': 'O jogo',
  'foot.col2': 'Referência',
  'foot.server': 'O que é o Refuge',
  'foot.start': 'Guia do novo jogador',
  'foot.join': 'Como entrar',
  'foot.faq': 'Perguntas e respostas',
  'foot.classes': 'Todas as 42 classes',
  'foot.newjobs': 'Bouncer e Pit Boss',
  'foot.mechanics': 'Combate e atributos',
  'foot.gear': 'Itens, refino, shadows',
  'foot.world': 'Regiões, masmorras, MVPs',
  'foot.changes': 'Mudanças em relação ao original',
  'foot.guides': 'Guias escritos por jogadores',
  'foot.llms': 'llms.txt',
  'foot.sitemap': 'Mapa do site',
  'foot.blurb': 'Um mundo gratuito para jogar, construído e mantido por um punhado ' +
    'de jogadores para quem quiser um lugar tranquilo para jogar.',
  'foot.legal': 'Return to Morroc: Refuge é um projeto de fãs, não oficial, sem ' +
    'qualquer afiliação, patrocínio ou endosso de nenhuma publicadora, desenvolvedora ' +
    'ou detentora de direitos. É gratuito para jogar, não aceita comércio por dinheiro ' +
    'real e nunca venderá poder dentro do jogo. Todos os nomes de terceiros que ' +
    'aparecem no site pertencem aos seus respectivos donos e são usados apenas para ' +
    'descrever a jogabilidade.<br><br>Feito pela comunidade, às claras. O conteúdo do ' +
    'site pode ser copiado livremente.',

  /* --- quick actions ---------------------------------------------------- */
  'quick.db': 'Database',
  'quick.dbSub': 'Todo item, todo monstro, todo drop',
  'quick.classes': 'Classes',
  'quick.classesSub': 'A árvore de jobs inteira',
  'quick.start': 'Comece aqui',
  'quick.startSub': 'Do nível 1 ao 130, em ordem',
  'quick.world': 'Mundo',
  'quick.worldSub': 'Masmorras e fim de jogo',

  /* --- home promises ---------------------------------------------------- */
  'home.p1t': 'Nunca pague para vencer',
  'home.p1': 'O servidor precisa se pagar e pagar quem o constrói, e isso será ' +
    'discutido abertamente com a comunidade. Seja lá o que for, não venderá poder ' +
    'e não venderá o seu tempo.',
  'home.p2t': 'Não existe build correta',
  'home.p2': 'Os sets travados por job que empurravam todo mundo para o mesmo ' +
    'estilo depois do nível 100 acabaram. Mais de cinquenta sets novos entraram no ' +
    'lugar, e nenhum pertence a um job.',
  'home.p3t': 'Construído à vista',
  'home.p3': 'Listas de balanceamento, árvores de skill e prazos perdidos são ' +
    'publicados antes do lançamento. O retorno da comunidade já mudou o projeto ' +
    'mais de uma vez.',

  /* --- database --------------------------------------------------------- */
  'db.h1': 'Database',
  'db.lede': 'Todo item e todo monstro, com a descrição que o próprio jogo ' +
    'mostra. Busque um nome, ou escolha uma categoria para navegar.',
  'db.items': 'Itens',
  'db.monsters': 'Monstros',
  'db.search': 'Buscar por nome ou efeito...',
  'db.more': 'Mais filtros',
  'db.extraWait': 'Abrir isto carrega os dados.',
  'db.startText': 'Nada é carregado até você pedir. Digite um nome ou um ' +
    'efeito acima, ou comece por um destes.',
  'db.reset': 'Limpar',
  'db.empty': 'Nada corresponde a esses filtros.',
  'db.note': '<strong>Estes são os dados vivos do jogo.</strong> Nomes, ' +
    'descrições e taxas de drop vêm direto do servidor em que o time está ' +
    'construindo, então são a referência mais precisa que existe. Ajustes de ' +
    'balanceamento chegam aqui conforme chegam no jogo. Onde uma página deste ' +
    'site disser algo diferente, ela é que vale. ' +
    '<a href="changes.html">Veja o que mudou</a>.',
  'db.note.link': 'Veja o que mudou',
  'foot.database': 'Itens e monstros',
  'foot.codex': 'O que as palavras significam',

  /* --- codex ------------------------------------------------------------ */
  'codex.h1': 'Codex',
  'codex.lede': 'As descrições de itens e habilidades são escritas para quem ' +
    'já joga. Estas são as palavras em que elas se apoiam, em português claro. ' +
    'Onde qualquer uma delas aparece no site, ela vem sublinhada na sua cor e ' +
    'aponta de volta para cá.',
  'codex.filter': 'Filtrar o codex...',
  'codex.empty': 'Nada com esse nome. Tente a database.',

  /* --- 404 -------------------------------------------------------------- */
  'lost.code': 'Erro 404',
  'lost.h1': 'Esta página se perdeu no caminho.',
  'lost.body': 'O endereço não existe, ou existia e mudou de lugar. Acontece com ' +
    'orfãos sem memória. Tente a busca, ou volte para um dos pontos de partida abaixo.',
  'lost.search': 'Buscar no site'
});
