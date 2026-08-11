const GRAMMAR_CARDS = [
  // Articles
  {id:"art-01",level:"A1",topic:"冠词",q:"法语有哪三类冠词？",a:"定冠词、不定冠词、部分冠词。",ex:"le / un / du",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-02",level:"A1",topic:"冠词",q:"不定冠词的阳性单数、阴性单数和复数分别是什么？",a:"阳性单数 <b>un</b>，阴性单数 <b>une</b>，复数统一用 <b>des</b>。",ex:"un livre, une table, des amis",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-03",level:"A1",topic:"冠词",q:"定冠词的阳性单数、阴性单数和复数分别是什么？",a:"阳性单数 <b>le</b>，阴性单数 <b>la</b>，复数统一用 <b>les</b>。",ex:"le livre, la table, les amis",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-04",level:"A1",topic:"冠词",q:"定冠词什么时候缩写成 l’？",a:"单数名词以元音或哑音 h 开头时，<b>le / la → l’</b>；性别并没有消失。",ex:"l’école (f.), l’hôtel (m.)",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-05",level:"A1",topic:"冠词",q:"部分冠词的四种基本形式是什么？",a:"阳性单数 <b>du</b>，阴性单数 <b>de la</b>，元音或哑音 h 前 <b>de l’</b>，复数 <b>des</b>。",ex:"du pain, de la soupe, de l’eau, des légumes",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-06",level:"A1",topic:"冠词",q:"定冠词和不定冠词在意义上的核心区别是什么？",a:"定冠词指双方已知、特定、唯一或泛指的一类事物；不定冠词引入未特指的一个或一些事物。",ex:"J’ai un chat. Le chat est noir.",src:"https://www.frenchcircles.ca/how-to-use-the-french-articles/"},
  {id:"art-07",level:"A1",topic:"冠词",q:"表达一般爱好或对一类事物的总体评价时，通常用什么冠词？",a:"通常用<b>定冠词</b>，而不是部分冠词。",ex:"J’aime le café. Les chiens sont fidèles.",src:"https://www.frenchcircles.ca/articles-grammar/"},
  {id:"art-08",level:"A1",topic:"冠词",q:"否定句中 un / une / des / du / de la 通常怎样变化？",a:"在 <b>ne…pas</b> 后通常变成 <b>de / d’</b>。",ex:"J’ai un vélo. → Je n’ai pas de vélo.",src:"https://www.frenchcircles.ca/the-negative-form/"},
  {id:"art-09",level:"A1",topic:"冠词",q:"être 后面的冠词在否定句中也变成 de 吗？",a:"通常不变。<b>être</b> 描述身份或性质时保留原冠词。",ex:"C’est un problème. → Ce n’est pas un problème.",src:"https://www.frenchcircles.ca/the-negative-form/"},
  {id:"art-10",level:"A1",topic:"冠词",q:"数量副词 beaucoup / peu / assez 后面接什么？",a:"接 <b>de / d’ + 名词</b>，一般不用 du、de la、des。",ex:"beaucoup de temps, peu d’argent",src:"https://www.frenchcircles.ca/les-adverbes-de-quantite/"},
  {id:"art-11",level:"A1",topic:"冠词",q:"à + le、à + les 分别缩合成什么？",a:"<b>au</b> 和 <b>aux</b>。à la、à l’ 不缩合。",ex:"au cinéma, aux États-Unis, à la gare",src:"https://www.frenchcircles.ca/the-preposition-a/"},
  {id:"art-12",level:"A1",topic:"冠词",q:"de + le、de + les 分别缩合成什么？",a:"<b>du</b> 和 <b>des</b>。de la、de l’ 不缩合。",ex:"du Canada, des enfants, de la France",src:"https://www.frenchcircles.ca/the-preposition-de/"},
  {id:"art-13",level:"A2",topic:"冠词",q:"des + 复数形容词 + 复数名词，在较正式书面语中常怎样变化？",a:"形容词位于名词前时，<b>des</b> 常变为 <b>de</b>。",ex:"de belles maisons",src:"https://www.frenchcircles.ca/les-vs-des-whats-the-difference/"},
  {id:"art-14",level:"A2",topic:"冠词",q:"职业、国籍或宗教作 être 的表语时，通常要不要不定冠词？",a:"没有修饰语时通常不用；有形容词等限定时常用冠词。",ex:"Elle est médecin. C’est une excellente médecin.",src:"https://www.frenchcircles.ca/cest-il-est-elle-est/"},

  // Gender, number, adjective agreement
  {id:"agr-01",level:"A1",topic:"性数配合",q:"法语名词的语法性别由什么决定？",a:"由词本身决定，不能只根据自然性别猜；学习名词时应连冠词一起记。",ex:"la voiture, le problème",src:"https://www.frenchcircles.ca/masculine-or-feminine-nouns/"},
  {id:"agr-02",level:"A1",topic:"性数配合",q:"名词变复数最常见的规则是什么？",a:"词尾加 <b>-s</b>；原本以 s、x、z 结尾通常不再变化。",ex:"une table → des tables; un prix → des prix",src:"https://www.frenchcircles.ca/masculine-or-feminine-nouns/"},
  {id:"agr-03",level:"A1",topic:"性数配合",q:"以 -al 结尾的名词常见复数变化是什么？",a:"多数 <b>-al → -aux</b>，但有例外要单记。",ex:"un travail → des travaux",src:"https://www.frenchcircles.ca/masculine-or-feminine-nouns/"},
  {id:"agr-04",level:"A1",topic:"性数配合",q:"形容词最基本的阴性和复数变化是什么？",a:"阴性通常加 <b>-e</b>，复数通常加 <b>-s</b>；已有相同词尾时可能不再加。",ex:"petit, petite, petits, petites",src:"https://www.frenchcircles.ca/french-adjectives/"},
  {id:"agr-05",level:"A2",topic:"性数配合",q:"-eux 结尾的形容词常怎样变阴性？",a:"通常 <b>-eux → -euse</b>。",ex:"heureux → heureuse",src:"https://www.frenchcircles.ca/types-of-adjectives/"},
  {id:"agr-06",level:"A2",topic:"性数配合",q:"大多数法语形容词放在名词前还是后？",a:"大多数放在名词后；表示美、年龄、好坏、大小等常见短形容词常置前。",ex:"une voiture rouge; un petit appartement",src:"https://www.frenchcircles.ca/bags-acronym-french-adjectives/"},
  {id:"agr-07",level:"B1",topic:"性数配合",q:"多个不同性别名词共用一个形容词时，传统规则如何配合？",a:"通常使用阳性复数。",ex:"Paul et Marie sont contents.",src:"https://www.frenchcircles.ca/french-adjectives-and-nouns/"},
  {id:"agr-08",level:"B1",topic:"性数配合",q:"过去分词与 être 构成复合时态时怎样配合？",a:"通常与主语性数配合。",ex:"Elle est arrivée. Ils sont partis.",src:"https://www.frenchcircles.ca/auxiliaire-etre-ou-avoir-passe-compose/"},
  {id:"agr-09",level:"B2",topic:"性数配合",q:"过去分词与 avoir 搭配时，什么时候与直接宾语配合？",a:"直接宾语位于过去分词<b>之前</b>时配合；位于之后通常不配合。",ex:"Les lettres que j’ai écrites. / J’ai écrit des lettres.",src:"https://www.frenchcircles.ca/accord-du-participe-passe-avec-avoir/"},

  // Sentence, questions, negation
  {id:"sen-01",level:"A1",topic:"句型与否定",q:"法语陈述句最基础的语序是什么？",a:"主语 + 变位动词 + 补语。",ex:"Marie parle français.",src:"https://www.frenchcircles.ca/construction-des-phrases/"},
  {id:"sen-02",level:"A1",topic:"句型与否定",q:"把陈述句变成一般疑问句，有哪三种常见方式？",a:"语调上扬；<b>est-ce que</b>；正式语体使用主谓倒装。",ex:"Tu viens ? / Est-ce que tu viens ? / Viens-tu ?",src:"https://www.frenchcircles.ca/the-interrogative-form/"},
  {id:"sen-03",level:"A1",topic:"句型与否定",q:"倒装疑问句什么时候插入 -t-？",a:"动词以元音结尾且主语是 il / elle / on 时，为便于发音插入 <b>-t-</b>。",ex:"Parle-t-il français ?",src:"https://www.frenchcircles.ca/lutilisation-du-t-dans-les-questions-en-francais/"},
  {id:"sen-04",level:"A1",topic:"句型与否定",q:"基本否定 ne…pas 放在哪里？",a:"围住变位动词；复合时态中围住助动词。",ex:"Je ne comprends pas. / Je n’ai pas compris.",src:"https://www.frenchcircles.ca/the-negative-form/"},
  {id:"sen-05",level:"A2",topic:"句型与否定",q:"ne…jamais、ne…plus、ne…rien 分别表示什么？",a:"从不、不再、什么也不。",ex:"Il ne vient jamais. Je ne veux plus rien.",src:"https://www.frenchcircles.ca/negative-words-in-french/"},
  {id:"sen-06",level:"A2",topic:"句型与否定",q:"ne…personne 中 personne 作主语时怎样说？",a:"<b>Personne ne + 动词</b>。",ex:"Personne ne répond.",src:"https://www.frenchcircles.ca/negative-words-in-french/"},
  {id:"sen-07",level:"A1",topic:"句型与否定",q:"c’est 和 il/elle est 的常见区别是什么？",a:"c’est 后常接名词或强调对象；il/elle est 后常直接接形容词、职业或国籍。",ex:"C’est un professeur. Il est patient. Il est français.",src:"https://www.frenchcircles.ca/cest-il-est-elle-est/"},
  {id:"sen-08",level:"A2",topic:"句型与否定",q:"qui 和 que 作为疑问词时，核心区别是什么？",a:"<b>qui</b> 问人；<b>que / quoi</b> 问事物。具体形式随句中功能和语体变化。",ex:"Qui vient ? Que fais-tu ? Tu fais quoi ?",src:"https://www.frenchcircles.ca/les-mots-interrogatifs/"},

  // Pronouns
  {id:"pro-01",level:"A1",topic:"代词",q:"法语主语人称代词有哪些？",a:"je, tu, il/elle/on, nous, vous, ils/elles。",ex:"On parle français.",src:"https://www.frenchcircles.ca/french-subject-pronouns/"},
  {id:"pro-02",level:"A1",topic:"代词",q:"tu 和 vous 怎样选择？",a:"tu 用于单个熟人或非正式关系；vous 用于复数对象，也用于单个陌生人或正式关系。",ex:"Comment allez-vous, Madame ?",src:"https://www.frenchcircles.ca/tu-or-vous/"},
  {id:"pro-03",level:"A2",topic:"代词",q:"直接宾语代词有哪些？",a:"me, te, le/la/l’, nous, vous, les。",ex:"Je vois Marie. → Je la vois.",src:"https://www.frenchcircles.ca/les-pronoms-objets-directs/"},
  {id:"pro-04",level:"A2",topic:"代词",q:"间接宾语代词 lui 和 leur 通常替代什么？",a:"替代 <b>à + 人</b>：lui 为单数，leur 为复数，不区分性别。",ex:"Je parle à Léa. → Je lui parle.",src:"https://www.frenchcircles.ca/les-pronoms-objets-indirects/"},
  {id:"pro-05",level:"A2",topic:"代词",q:"y 通常替代什么？",a:"替代地点，或 <b>à + 事物</b>；一般不替代人。",ex:"Je vais à Paris. → J’y vais.",src:"https://www.frenchcircles.ca/les-pronoms-objets-en-et-y/"},
  {id:"pro-06",level:"A2",topic:"代词",q:"en 通常替代什么？",a:"替代 <b>de + 名词</b>、部分冠词结构或数量所指对象；数量词通常保留。",ex:"Tu as des frères ? Oui, j’en ai deux.",src:"https://www.frenchcircles.ca/les-pronoms-objets-en-et-y/"},
  {id:"pro-07",level:"A2",topic:"代词",q:"宾语代词通常放在变位动词的什么位置？",a:"通常放在变位动词前；肯定命令式是重要例外，放在动词后。",ex:"Je le vois. / Regarde-le !",src:"https://www.frenchcircles.ca/les-pronoms-objets/"},
  {id:"pro-08",level:"B1",topic:"代词",q:"双宾语代词在普通陈述句中的常见顺序是什么？",a:"me/te/se/nous/vous → le/la/les → lui/leur → y → en。",ex:"Je le lui donne.",src:"https://www.frenchcircles.ca/les-pronoms-objets/"},
  {id:"pro-09",level:"B1",topic:"代词",q:"celui、celle、ceux、celles 是什么？",a:"指示代词，分别对应阳单、阴单、阳复、阴复；后面常接 de 或关系从句。",ex:"Celui de Paul; celles qui arrivent",src:"https://www.frenchcircles.ca/demonstrative-pronouns/"},
  {id:"pro-10",level:"B1",topic:"代词",q:"qui、que、dont、où 作为关系代词时分别承担什么功能？",a:"qui 作主语；que 作直接宾语；dont 替代 de 结构；où 表地点或时间。",ex:"Le livre que je lis; la femme dont je parle",src:"https://www.frenchcircles.ca/french-grammar-level-4/"},

  // Prepositions and adverbs
  {id:"prep-01",level:"A1",topic:"介词与副词",q:"去城市、来自城市分别怎样表达？",a:"去：<b>à + 城市</b>；来自：<b>de/d’ + 城市</b>。",ex:"à Paris; de Montréal",src:"https://www.frenchcircles.ca/prepositions/"},
  {id:"prep-02",level:"A2",topic:"介词与副词",q:"去阳性国家、阴性国家、复数国家常分别用什么？",a:"阳性国家常用 <b>au</b>，阴性国家常用 <b>en</b>，复数国家用 <b>aux</b>。",ex:"au Canada, en France, aux États-Unis",src:"https://www.frenchcircles.ca/prepositions/"},
  {id:"prep-03",level:"A2",topic:"介词与副词",q:"chez 的核心用法是什么？",a:"表示在某人家、某类人的场所或某专业人士处。",ex:"chez moi, chez le médecin",src:"https://www.frenchcircles.ca/chez-moi-chez-toi-chez-lui-chez-elle-chez-nous/"},
  {id:"prep-04",level:"B1",topic:"介词与副词",q:"depuis 表达持续时间时，动词通常用什么时态？",a:"动作从过去开始并持续到现在时，通常用<b>现在时</b>。",ex:"J’habite ici depuis trois ans.",src:"https://www.frenchcircles.ca/depuis-pendant-pour-il-y-a/"},
  {id:"prep-05",level:"B1",topic:"介词与副词",q:"pendant、pour、il y a 的时间意义有什么区别？",a:"pendant 表实际持续时长；pour 表计划或预期时长；il y a 表“多久以前”。",ex:"pendant deux heures; pour une semaine; il y a trois jours",src:"https://www.frenchcircles.ca/depuis-pendant-pour-il-y-a/"},
  {id:"prep-06",level:"A2",topic:"介词与副词",q:"规则方式副词通常怎样由形容词构成？",a:"常在形容词阴性形式后加 <b>-ment</b>。",ex:"heureuse → heureusement",src:"https://www.frenchcircles.ca/les-adverbes-de-maniere/"},
  {id:"prep-07",level:"B1",topic:"介词与副词",q:"bon / bien 与 mauvais / mal 的基本区别是什么？",a:"bon、mauvais 多修饰名词；bien、mal 多修饰动词。",ex:"un bon repas; il travaille bien",src:"https://www.frenchcircles.ca/bon-bien-mauvais-mal-meilleur-mieux/"},
  {id:"prep-08",level:"B1",topic:"介词与副词",q:"meilleur 和 mieux 分别是什么的比较级？",a:"meilleur 是 <b>bon</b> 的比较级，修饰名词；mieux 是 <b>bien</b> 的比较级，修饰动词。",ex:"un meilleur choix; elle chante mieux",src:"https://www.frenchcircles.ca/bon-bien-mauvais-mal-meilleur-mieux/"},

  // Present and verb system
  {id:"verb-01",level:"A1",topic:"动词系统",q:"动词不定式和变位形式的区别是什么？",a:"不定式是词典形式，不标人称；变位形式随主语、时态和语气改变。",ex:"parler → nous parlons",src:"https://www.frenchcircles.ca/infinitive-vs-conjugated-verbs-in-french/"},
  {id:"verb-02",level:"A1",topic:"动词系统",q:"规则 -er 动词现在时六个人称词尾是什么？",a:"-e, -es, -e, -ons, -ez, -ent。",ex:"je parle, nous parlons, ils parlent",src:"https://www.frenchcircles.ca/er-verbs/"},
  {id:"verb-03",level:"A1",topic:"动词系统",q:"规则第二组 -ir 动词现在时六个人称词尾是什么？",a:"-is, -is, -it, -issons, -issez, -issent。",ex:"je finis, nous finissons",src:"https://www.frenchcircles.ca/french-ir-verbs-with-phonetic-pronunciation/"},
  {id:"verb-04",level:"A1",topic:"动词系统",q:"规则 -re 动词现在时六个人称词尾是什么？",a:"-s, -s, 无词尾, -ons, -ez, -ent。",ex:"je vends, il vend, ils vendent",src:"https://www.frenchcircles.ca/french-re-verbs-with-phonetic-pronunciation/"},
  {id:"verb-05",level:"A2",topic:"动词系统",q:"代词式动词现在时的结构是什么？",a:"主语 + 对应反身代词 + 变位动词。",ex:"je me lève, nous nous levons",src:"https://www.frenchcircles.ca/french-reflexive-verbs/"},
  {id:"verb-06",level:"A2",topic:"动词系统",q:"venir de + 不定式表示什么？",a:"最近过去时，表示“刚刚做了某事”。",ex:"Je viens de finir.",src:"https://www.frenchcircles.ca/recent-past-venir-de-infinitive/"},
  {id:"verb-07",level:"B1",topic:"动词系统",q:"être en train de + 不定式表示什么？",a:"强调动作正在进行。",ex:"Je suis en train de travailler.",src:"https://www.frenchcircles.ca/etre-en-train-de/"},

  // Past tenses
  {id:"past-01",level:"A2",topic:"过去时",q:"passé composé 的基本结构是什么？",a:"现在时的 avoir 或 être + 过去分词。",ex:"J’ai parlé. Elle est partie.",src:"https://www.frenchcircles.ca/le-passe-compose/"},
  {id:"past-02",level:"A2",topic:"过去时",q:"规则 -er、-ir、-re 动词的过去分词通常怎样构成？",a:"-er → -é；-ir → -i；-re → -u。",ex:"parlé, fini, vendu",src:"https://www.frenchcircles.ca/les-participes-passes/"},
  {id:"past-03",level:"A2",topic:"过去时",q:"哪些动词在 passé composé 中常用 être？",a:"主要是部分位移动词和全部代词式动词；其余多数用 avoir。",ex:"elle est venue; ils se sont levés",src:"https://www.frenchcircles.ca/dr-mrs-vandertramp/"},
  {id:"past-04",level:"A2",topic:"过去时",q:"imparfait 怎样构成？",a:"取现在时 nous 形式去掉 -ons，加 -ais, -ais, -ait, -ions, -iez, -aient；être 词干为 ét-。",ex:"nous parlons → je parlais",src:"https://www.frenchcircles.ca/limparfait/"},
  {id:"past-05",level:"B1",topic:"过去时",q:"passé composé 和 imparfait 的核心对立是什么？",a:"passé composé 推进已完成事件；imparfait 描写背景、状态、习惯或正在进行的动作。",ex:"Il pleuvait quand je suis sorti.",src:"https://www.frenchcircles.ca/present-imparfait-passe-compose-practice/"},
  {id:"past-06",level:"B1",topic:"过去时",q:"plus-que-parfait 的结构和作用是什么？",a:"imparfait 的 avoir/être + 过去分词，表示另一个过去动作之前已经完成。",ex:"Il avait déjà mangé quand je suis arrivé.",src:"https://www.frenchcircles.ca/le-plus-que-parfait/"},
  {id:"past-07",level:"B1",topic:"过去时",q:"代词式动词的复合过去时基本语序是什么？",a:"主语 + 反身代词 + être + 过去分词。配合还要看反身代词的句法功能。",ex:"Elle s’est levée.",src:"https://www.frenchcircles.ca/les-verbes-pronominaux-au-passe-compose/"},
  {id:"past-08",level:"B2",topic:"过去时",q:"描述过去背景时，哪些提示常指向 imparfait？",a:"过去的习惯、持续状态、天气、时间、年龄和“当时正在……”常用 imparfait。",ex:"Tous les jours, il marchait. Il faisait froid.",src:"https://www.frenchcircles.ca/indicators-for-imparfait/"},

  // Future and conditional
  {id:"fut-01",level:"A2",topic:"将来与条件式",q:"futur proche 的结构和常见意义是什么？",a:"aller 现在时 + 不定式，表示近期或已有迹象、计划的将来。",ex:"Je vais partir.",src:"https://www.frenchcircles.ca/le-futur-proche/"},
  {id:"fut-02",level:"B1",topic:"将来与条件式",q:"futur simple 怎样构成？",a:"多数动词用完整不定式作词干，-re 去掉末尾 e，再加 -ai, -as, -a, -ons, -ez, -ont。",ex:"je parlerai; je vendrai",src:"https://www.frenchcircles.ca/le-futur-simple/"},
  {id:"fut-03",level:"B1",topic:"将来与条件式",q:"常见不规则将来时词干有哪些？",a:"être ser-, avoir aur-, aller ir-, faire fer-, venir viendr-, pouvoir pourr-, vouloir voudr-, devoir devr-。",ex:"nous serons; ils viendront",src:"https://www.frenchcircles.ca/irregular-verbs-in-future-tense/"},
  {id:"fut-04",level:"B1",topic:"将来与条件式",q:"conditionnel présent 怎样构成？",a:"使用 futur simple 的词干，加 imparfait 的词尾。",ex:"je parlerais, nous viendrions",src:"https://www.frenchcircles.ca/le-conditionnel-present/"},
  {id:"fut-05",level:"B1",topic:"将来与条件式",q:"si + imparfait 后面通常搭配什么？",a:"主句通常用 conditionnel présent，表达与现在或将来相反、假设的情况。",ex:"Si j’avais le temps, je voyagerais.",src:"https://www.frenchcircles.ca/could-should-would/"},
  {id:"fut-06",level:"B2",topic:"将来与条件式",q:"futur antérieur 的结构和作用是什么？",a:"futur simple 的 avoir/être + 过去分词，表示在未来某时之前已经完成。",ex:"Quand tu arriveras, j’aurai fini.",src:"https://www.frenchcircles.ca/le-futur-anterieur/"},
  {id:"fut-07",level:"B2",topic:"将来与条件式",q:"si 从句能直接使用 futur simple 或 conditionnel 吗？",a:"表示条件的 si 从句通常不用 futur 或 conditionnel；常见搭配是现在时 + 将来时，或 imparfait + conditionnel。",ex:"Si tu viens, nous sortirons.",src:"https://www.frenchcircles.ca/french-grammar-level-7/"},

  // Subjunctive and non-finite forms
  {id:"sub-01",level:"B1",topic:"虚拟式与非限定形式",q:"subjonctif présent 常由哪类主句触发？",a:"常由意愿、必要、情感、怀疑、评价等主观表达加 que 触发。",ex:"Il faut que tu viennes.",src:"https://www.frenchcircles.ca/le-subjonctif-present/"},
  {id:"sub-02",level:"B1",topic:"虚拟式与非限定形式",q:"现在虚拟式多数动词怎样取词干？",a:"通常取 ils 现在时形式去掉 -ent，接 -e, -es, -e, -ions, -iez, -ent；nous/vous 有时使用 nous 词干。",ex:"ils parlent → que je parle",src:"https://www.frenchcircles.ca/le-subjonctif-present/"},
  {id:"sub-03",level:"B1",topic:"虚拟式与非限定形式",q:"avant que 和 après que 后面分别倾向用什么语气？",a:"avant que 通常接虚拟式；规范语法中 après que 接直陈式。",ex:"avant qu’il parte; après qu’il est parti",src:"https://www.frenchcircles.ca/avant-que-subjonctif-apres-que-indicatif/"},
  {id:"sub-04",level:"B2",topic:"虚拟式与非限定形式",q:"主句和从句主语相同时，很多“介词 + que + 虚拟式”结构可怎样简化？",a:"常改为介词短语 + 不定式。",ex:"avant de partir; pour réussir",src:"https://www.frenchcircles.ca/le-subjonctif-present/"},
  {id:"sub-05",level:"B1",topic:"虚拟式与非限定形式",q:"participe présent 的常见构成是什么？",a:"取 nous 现在时去掉 -ons，加 <b>-ant</b>；avoir、être、savoir 分别为 ayant、étant、sachant。",ex:"nous parlons → parlant",src:"https://www.frenchcircles.ca/french-present-participle/"},
  {id:"sub-06",level:"B2",topic:"虚拟式与非限定形式",q:"gérondif 怎样构成，常表示什么？",a:"<b>en + participe présent</b>，常表示方式、同时发生或条件。",ex:"Il apprend en lisant.",src:"https://www.frenchcircles.ca/french-present-participle/"},

  // Advanced syntax and discourse
  {id:"adv-01",level:"B1",topic:"进阶句法",q:"COD 和 COI 的区别是什么？",a:"COD 直接跟在动词后无介词；COI 由 à、de 等介词引出。",ex:"Je vois Paul (COD). Je parle à Paul (COI).",src:"https://www.frenchcircles.ca/le-complement-dobjet-direct-cod/"},
  {id:"adv-02",level:"B1",topic:"进阶句法",q:"直接引语改间接引语时，陈述句通常用什么连接词？",a:"通常用 <b>que</b>；一般疑问句常用 si，疑问词问句保留相应疑问词。",ex:"Il dit : « Je viens. » → Il dit qu’il vient.",src:"https://www.frenchcircles.ca/indirect-speech-le-discours-indirect/"},
  {id:"adv-03",level:"B2",topic:"进阶句法",q:"过去时主句中的间接引语，présent 常发生什么时态后移？",a:"常后移为 imparfait；passé composé 常后移为 plus-que-parfait；futur 常后移为 conditionnel。",ex:"Il a dit : « Je viendrai. » → Il a dit qu’il viendrait.",src:"https://www.frenchcircles.ca/indirect-speech-le-discours-indirect/"},
  {id:"adv-04",level:"B1",topic:"进阶句法",q:"比较级“比……更 / 更少 / 一样”怎样构成？",a:"plus / moins / aussi + 形容词或副词 + que。名词和动词的结构略有不同。",ex:"plus rapide que; aussi bien que",src:"https://www.frenchcircles.ca/french-grammar-level-5/"},
  {id:"adv-05",level:"B1",topic:"进阶句法",q:"最高级怎样构成？",a:"定冠词 + plus / moins + 形容词；形容词仍需与名词性数配合。",ex:"la plus grande ville",src:"https://www.frenchcircles.ca/french-grammar-level-5/"},
  {id:"adv-06",level:"B2",topic:"进阶句法",q:"au fait、en fait、en effet 的区别是什么？",a:"au fait 常用于“顺便说/说到这个”；en fait 表“其实/事实上”并修正信息；en effet 表“确实/因为”，用于确认或解释。",ex:"Au fait, tu viens ? En fait, je suis occupé. En effet, je travaille.",src:"https://www.frenchcircles.ca/au-fait-en-fait-en-effet/"},
  {id:"adv-07",level:"B2",topic:"进阶句法",q:"法语口语与正式书面语在否定结构上最明显的差异是什么？",a:"口语常省略 ne；正式书面语通常保留 ne。考试写作应保留完整否定。",ex:"Je sais pas. / Je ne sais pas.",src:"https://www.frenchcircles.ca/differences-entre-loral-et-lecrit/"},
  {id:"adv-08",level:"B2",topic:"进阶句法",q:"使句子衔接更清楚，至少应掌握哪几类连接关系？",a:"增补、对比、原因、结果、让步、举例、顺序和总结。",ex:"de plus, pourtant, puisque, donc, bien que, par exemple, enfin",src:"https://www.frenchcircles.ca/how-to-say-simple-french-sentences-in-different-ways/"}
];
