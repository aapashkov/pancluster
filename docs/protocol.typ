#align(center, text(16pt)[
  *El panclúster como método de análisis de la diversidad metabólica en los
   microorganismos: Un estudio de caso en _Fusarium_*
])

#align(center)[
  Anton Pashkov \
  ENES Morelia, UNAM \
  #link("mailto:pashkov@comunidad.unam.mx")
]

#grid(
  columns: (1fr, 1fr),
  align(center)[
    *Tutora* \
    Nelly Sélem Mojica \
    Centro de Ciencias Matemáticas, UNAM \
    #link("mailto:nselem@matmor.unam.mx")
  ],
  align(center)[
    *Co-tutor* \
    José Manuel Villalobos Escobedo \
    Instituto de Investigación sobre Obesidad, ITESM \
    #link("mailto:jose.villalobos@tec.mx")
  ]
)

#set par(justify: true)
#set text(hyphenate: true, lang: "es")

= Introducción

Uno de los grupos de hongos de mayor relevancia en la investigación agrícola es
_Fusarium_, un género muy diverso capaz de adaptarse rápidamente y provocar daño
físico considerable a muchas plantas, así como de producir micotoxinas que
pueden contaminar los alimentos, poniendo en riesgo la salud del ser humano y de
los animales @ekwomadu2023. El alto grado de patogenicidad y adaptación de
_Fusarium_ se explica en parte por su diversidad metabólica, la cual se
caracteriza por su capacidad de producir un sin número de metabolitos
secundarios o especializados, que son compuestos orgánicos que no están
involucrados de manera directa en las funciones básicas como el crecimiento y la
reproducción, sino que se encargan de realizar funciones especializadas tales
como la síntesis de antibióticos, la defensa contra patógenos y el parasitismo
@luckner1990. Al igual que casi todas las sustancias en los organismos vivos,
los metabolitos secundarios son producidos por enzimas, cada una de las cuales
es codificada por un gen, es decir, un segmento específico del ADN del
organismo. En microorganismos como los hongos y las bacterias, los genes que
codifican para las enzimas de las vías metabólicas especializadas se encuentran
cerca entre sí @fondi2024; por ello, a estos conjuntos de genes se les conoce
como clústeres de genes biosintéticos (BGCs, por _Biosynthetic Gene Clusters_). 
Múltiples estudios sobre diferentes especies de _Fusarium_ han demostrado el 
importante papel que desempeñan los BGCs en su adaptabilidad y patogenicidad en
las plantas. Por ejemplo, #cite(<pokhrel2023>, form: "prose") identificaron
varios BGCs en muestras pertenecientes a la especie _Fusarium solani_ que
codiﬁcan para sustancias como policétidos, péptidos no ribosómicos y terpenos,
todas implicadas en su habilidad de infectar una amplia gama de huéspedes. Por
su parte, #cite(<hoogendoorn2018>, form: "prose") compararon los BGCs de ocho
cepas de distintas especies de _Fusarium_, encontrando que el repertorio de BGCs
refleja la patogenicidad de la cepa y que muchos BGCs en _Fusarium_ están
duplicados en cromosomas extra, lo que les da la libertad de experimentar
procesos evolutivos manteniendo la función original del BGC intacta. Estos
antecedentes indican que los hongos del género _Fusarium_ son buenos modelos
para entender la evolución de los BGCs dependiendo de las condiciones ambientes.
Así, en el presente trabajo me enfocaré en el estudio de los BGCs de dos
especies de _Fusarium_: _F. chlamydosporum_ y _F. oxysporum_.

En 2019, un campo de cultivo de fresa en Irapuato, Guanajuato, experimentó una
grave infección fúngica. Un grupo de investigación se dio la tarea de
identificar a los organismos responsables por medio de sus marcadores
moleculares, y los resultados de su trabajo fueron entregados a mi co-tutor
Manuel Villalobos (comunicación personal, s. f.). Un marcador molecular es una
secuencia de ADN en un organismo que permite distinguir la especie (o cualquier
otra categoría taxonómica, como el género o la subespecie) a la que pertenece
@betsy2023. En los hongos, el marcador molecular por excelencia para delimitar
especies es el espaciador transcrito interno o ITS @suneja2023. El grupo de
investigación obtuvo las secuencias del ITS de las muestras aisladas, las
comparó con las secuencias del ITS conocidas, y construyó un árbol filogenético
(@its-phylogeny). Los investigadores encontraron que son varias las especies
involucradas y la filogenia reconstruida sugiere la especie a la que pertenece
cada muestra: F9 y F11 pertenecen a _F. oxysporum_; F13, F17 y F19 son
cepas de _Fusarium equiseti_; F6 es _Fusarium chlamydosporum_; WT es
_Trichoderma atroviride_; y F18 es _Mortierella chienii_. El ITS suele ser
insuficiente para discriminar muchas de las especies de _Fusarium_, y se sugiere
emplear marcadores alternativos tales como la ß-tubulina, o bien, usar
combinaciones de marcadores, luego de haber empleado el ITS @alhatmi2016. El
grupo optó por utilizar la ß-tubulina como marcador, con lo cual se confirmaron
las especies encontradas con el ITS. De todas las cepas identificadas, las que
tuvieron una mayor propagación por el campo fueron F6 y F11, por lo que se
decidió secuenciar su genoma completo.

#figure(
  image("assets/its-phylogeny.png", width: 80%),
  caption: [
    Filogenia de las secuencias del ITS de las muestras recolectadas del campo
    de cultivo junto con algunas secuencias del ITS conocidas de hongos. Las
    muestras del campo son las que empiezan con F seguido de un número, y la de
    WT. La distancia entre las terminaciones del árbol representa qué tan
    diferentes son dos secuencias y los números en cada bifurcación es el
    _bootstrap_, un valor de 0 a 100 que indica qué tan confiable es el clado
    que se genera con dicha bifurcación (un clado es una bifurcación, o
    ancestro, y todos sus descendientes). Durante la construcción de árboles
    filogenéticos, se prueban múltiples configuraciones de las ramas, pero la
    que se reporta es la que mejor describe las distancias y relaciones entre
    las secuencias, y los números _bootstrap_ muestran en cuántas de las
    configuraciones probadas existe cada ramificación. Para esta filogenia en
    particular, se probaron 100 configuraciones diferentes.
  ]
) <its-phylogeny>

Llamamos genoma a la totalidad de la información genética contenida dentro de un
organismo @heckel2003. La tarea de determinar la composición de un genoma se
conoce como secuenciación. En la actualidad, existen múltiples tecnologías de
secuenciación generalmente divididas en tres generaciones. Sin embargo, lo que
es común a todas las tecnologías es que no es posible obtener la secuencia
genómica completa, sino sólo fragmentos, cuya longitud depende de la tecnología
utilizada @camargo2020. Posteriormente a la secuenciación, estos fragmentos,
llamados lecturas, se ensamblan por solapamiento para producir secuencias más
largas llamadas contigs, que representan el genoma reconstruido del organismo.
Varias lecturas se pueden solapar en una misma región; al número de lecturas que
se ensamblan en una posición particular se le conoce como profundidad.
Idealmente, el número de contigs obtenidos coincide con la cantidad de
cromosomas que posee el organismo, pero en muchos casos, se consiguen genomas
más fragmentados. Decimos que se realiza un ensamblado híbrido cuando se
ensamblan lecturas provenientes de tecnologías diferentes @chen2020. Junto con
nuestros colaboradores, secuenciamos —pero sin ensamblar— los genomas de F6 y
F11 utilizando dos tecnologías diferentes para cada muestra: una de lecturas
cortas y otra de lecturas largas. Tanto la muestra F6 como F11 fueron
secuenciadas con una tecnología llamada Illumina MiSeq, la cual permite obtener
lecturas cortas (de longitud 300\) por un precio relativamente barato comparado
con otras tecnologías de Illumina, pero el número de lecturas producido
—específicamente de 1 a 25 millones— es más bajo. La muestra F6, como se
explicará en el párrafo siguiente, pertenece a una especie poco estudiada, por
lo que fue posteriormente resecuenciada para obtener lecturas cortas de mejor
calidad mediante una tecnología diferente denominada Illumina NovaSeq, que es
más cara y produce lecturas ligeramente más cortas (de longitud 150\) que MiSeq,
pero permite obtener un mayor número de lecturas —más de mil millones—, por lo
que la profundidad conseguida es mucho mayor. Algo que caracteriza a los genomas
de los hongos es que presentan largas regiones repetitivas que son imposibles de
ensamblar con lecturas tan cortas. Por ello, también se extrajeron las lecturas
largas de ambas muestras con otra tecnología denominada Oxford Nanopore.

¿Qué se sabe sobre las especies identificadas en el campo de cultivo mexicano?
_Fusarium chlamydosporum_, a pesar de ser capaz de provocar marchitez en plantas
como el chile y la berenjena @parihar2022, permanece poco explorado
genómicamente hablando cuando se compara con otras especies de _Fusarium_ tales
como _Fusarium oxysporum_. Esto se refleja en el hecho de que, hasta octubre de
2024, sólo existe un genoma de _F. chlamydosporum_ disponible en la base de
datos de GenBank @clark2016 con el código de accesión GCA\_014898915.1. Este
genoma fue extraído de una cepa presente en el suelo de un campo de cultivo de
maíz de Australia. Por lo tanto, una de las labores de este trabajo es la
introducción del segundo genoma para esta especie, y la comparación entre una
cepa de _F. chlamydosporum_ de México que infecta a la fresa y otra de Australia
que infecta al maíz es, en sí, un paso adelante en la elucidación de la
naturaleza genómica de esta misteriosa especie respecto a dos áreas geográficas
y dos huéspedes diferentes.

Por su parte, _Fusarium oxysporum_ tuvo una suerte totalmente diferente. Una de
las enfermedades históricamente más notorias en las plantas, la enfermedad de
Panamá, obligó a la humanidad, a mediados del siglo XX, a cambiar de variedad de
plátano de la Gros Michel a la Cavendish, que es la variedad más consumida en la
actualidad. _F. oxysporum_ fue el agente causal de esta enfermedad, y desde
entonces ha sido una de las especies de hongo de mayor interés en el estudio de
la patología de las plantas @ploetz2015. Se trata de un organismo capaz de
parasitar tanto las raíces como las copas de todo tipo de plantas, aunque
también puede ser de vida libre o endofítico no parasítico (es decir, que vive
dentro de una planta sin provocarle daño alguno). Sin embargo, cada individuo
sólo muestra patogenicidad hacia grupos específicos de plantas. Por ello, las
cepas de _F. oxysporum_ se agrupan en las llamadas _formae speciales_ (abreviado
_ff. spp._; en singular _forma specialis_, o _f. sp._), cada una de las cuales
se especializa en parasitar a un huésped o conjunto de huéspedes en particular.
Por ejemplo, _F. oxysporum f. sp. fragariae_ es el nombre designado a aquéllas
cepas que parasiten a la fresa, _f. sp. lycopersici_ es la forma especial
adaptada al jitomate, y _f. sp. cubense_ ataca específicamente al espárrago y al
plátano (como es el caso de la enfermedad de Panamá).

Es posible determinar la _forma specialis_ a la que pertenece una cepa a través
de experimentos controlados donde se inoculan cepas sobre diferentes plantas y
se observan los síntomas resultantes. No obstante, estudios recientes han
buscado identificar marcadores moleculares que permitan distinguir a las _formae
speciales_. Esta tarea ha resultado ser muy difícil por dos razones: (1) las
_formae speciales_ no tienen un origen evolutivo común, y (2) las cepas de _F.
oxysporum_ de vida libre y las endofíticas no parasíticas son de alta
variabilidad genética y suelen estar estrechamente relacionadas con las formas
patógenas. A pesar de esto, ya se ha logrado identificar múltiples marcadores
para distinguir algunas de las formas, tales como el factor de elongación de la
traducción 1-α (TEF1), el espaciador intergénico ribosómico (IGS), el tamaño de
las inserciones de los transposones, y los genes que codifican para proteínas
secretadas en el xilema o SIX @edel2019. Con este proyecto de tesis, se busca
proponer y evaluar un nuevo método para distinguir a las _formae speciales_ por
medio de los genes presentes en sus BGCs, y la manera en la que se logrará esto
se resume en el párrafo siguiente.

Hoy en día, gracias a los avances técnicos, es posible realizar estudios donde
se comparan múltiples genomas al mismo tiempo. Una manera de hacer esto es con
la pangenómica. Introducido por #cite(<tettelin2005>, form: "prose"), el
concepto de pangenoma hace referencia al conjunto de todos los genes de todas
las cepas de un clado —donde un clado es un grupo de organismos con un ancestro
común reciente. Esencialmente, se busca construir un diagrama de Venn de los
genes de todos los genomas agrupando los genes en familias, donde cada familia
de genes es un conjunto de genes localizados en uno o varios genomas, y cuyas
secuencias y funciones son similares. De acuerdo a la localización de las
familias de genes en los genomas, el pangenoma se divide en tres partes: (1) el
“core”, que contiene las familias de genes presentes en todos los genomas, (2)
el “shell”, que comprende a las familias de genes que están en algunos pero no
todos los genomas, y (3) el “cloud”, en el que están las familias de genes
encontradas en sólo un genoma. La importancia de la pangenómica radica en que
permite capturar el espectro completo de la variación genética dentro de un
grupo de organismos, lo que es crucial cuando se estudian caracteres y
enfermedades complejas @makinen2023. Una de las propuestas del presente proyecto
es aplicar las técnicas de pangenómica sobre los BGCs. Al igual que los genes,
los BGCs también pueden ser agrupados en familias de BGCs (abreviadas GCFs, por
_Gene Cluster Families_) de acuerdo a su similitud de secuencia y función.
Existen múltiples algoritmos que calculan las GCFs de un conjunto de BGCs, tales
como BiG-SCAPE @navarro2020 y BiG-SLiCE @kautsar2021. A partir de los GCFs, es
posible reconstruir una estructura similar a la de un pangenoma, pero ahora
utilizando los BGCs como si fueran los genomas. Por tanto, de cada GCF es
posible extraer un pangenoma, que de ahora en adelante se nombrará _panclúster_,
ya que hace referencia a un pangenoma de una familia de clústeres biosintéticos.

Así, dado que los BGCs influyen en la patogenicidad y adaptabilidad de _F.
oxysporum_, las distintas _formae speciales_ de dicha especie deben poseer
características distintivas en sus BGCs que les proveen la capacidad de
parasitar a plantas específicas. Por lo tanto, al reconstruir todos los
panclústeres de la especie, obtenemos información sobre no sólo los BGCs
característicos de cada _forma specialis_, sino también qué genes están
presentes y cuáles no. Dicha información puede entonces funcionar como entrada
para modelos comparativos y de predicción que permitan diferenciar a las _formae
speciales_. En otras palabras, se plantea un problema de clasificación
multiclase para las _formae speciales_ de _F. oxysporum_ empleando los BGCs como
datos de entrenamiento. Para _Fusarium chlamydosporum_, será imposible
reproducir este proceso debido a que sólamente hay dos genomas disponibles, pero
la comparación entre ellos aún así es importante debido a que la fuente de cada
una de las cepas es muy distinta, tal como se había explicado anteriormente.
Explorar, visualizar y modelar los panclústeres respecto a las _formae
speciales_ de _Fusarium oxysporum_, y comparar los dos genomas de _Fusarium
chlamydosporum_, requerirá del empleo de múltiples tareas de aprendizaje
automático tanto supervisado como no supervisado, así como buenas prácticas de
análisis de datos, lo que justifica la relación entre este trabajo y lo
aprendido durante la licenciatura.

= Descripción de la tarea a realizar

Este proyecto será un trabajo de exploración de la diversidad metabólica de dos
especies de hongos —_Fusarium oxysporum_ y _Fusarium chlamydosporum_— para las
cuales se tienen dos cepas mexicanas nuevas. Para _F. chlamydosporum_, se
buscará comparar la cepa mexicana con la única cepa de esta especie cuyo genoma
se encuentra disponible hasta el momento. Para _F. oxysporum_, se plantea el
desarrollo de un método de análisis genómico para predecir la _forma specialis_
a la que pertenece una cepa dada por medio de la reconstrucción de sus
panclústeres. La hipótesis es que la presencia y ausencia de genes específicos
dentro de los clústeres biosintéticos de _F. oxysporum_ es suficiente para
diferenciar entre sus _formae speciales_. La confirmación de dicha hipótesis da
paso a otra importante pregunta de investigación que se abordará en el presente
proyecto de tesis: ¿qué clústeres biosintéticos son clave en la diferenciación
entre las _formae speciales_ de _F. oxysporum_?

= Objetivo general

Estudiar la diversidad metabólica de _Fusarium_ mediante el análisis de sus
panclústeres, con énfasis en dos especies y dos muestras de un campo de cultivo
mexicano, para la estimar la influencia que posee el metabolismo especializado
sobre la adaptación de _Fusarium_ a huéspedes específicos.

= Objetivos particulares

+ Caracterizar los genomas de dos muestras de _Fusarium_ provenientes de un
  campo de cultivo de fresa en Irapuato, Guanajuato, para su comparación con los
  genomas de _Fusarium_ asociados a otros ambientes y huéspedes.  
+ Describir las familias de clústeres biosintéticos más relevantes para la
  diferenciación entre diez formas especiales de _F. oxysporum_.  
+ Determinar el grado de influencia que tiene el metabolismo especializado sobre
  la adaptabilidad de _F. oxysporum_ a diferentes huéspedes vegetales.

= Metodología

== Recursos

Se dispone de un servidor de Ubuntu 22.04 con 32 procesadores y 125 Gb de RAM.

== Actividades a realizar

Primeramente, se limpiarán las lecturas de Illumina con TrimGalore @krueger2023
y las de Oxford Nanopore con Porechop @wick2017 y Chopper @decoster2023. El
ensamblado se realizará probando múltiples _pipelines_ destinados para ello,
como hybridSPAdes @antipov2016 y MaSuRCA @zimin2013, así como estrategias
manuales para combinar los ensamblados de lecturas cortas con los de lecturas
largas. Se tomará como mejor ensamblado aquél que tenga las mejores evaluaciones
por BUSCO @manni2021, un programa que mide la completitud de los ensamblados
midiendo los contigs y contando el número de genes que presenta respecto al
total que debería tener según una referencia. Específicamente, se configurará
BUSCO para que realice la comparación con Hypocreales, que es el orden al que
pertenece _Fusarium_.

La muestra F6, que según los análisis filogenéticos previos, es _Fusarium
chlamydosporum_, por lo que será comparada con el genoma de referencia de dicha
especie. En tanto que la muestra F11 se comparará con el genoma de referencia de
_F. oxysporum_. En ambos casos, se incluirán algunas otras especies dentro y
fuera del género _Fusarium_ con el fin de identificar las características que
son exclusivas de _Fusarium_. Para lograr esto, primero se van a enmascarar las
secuencias repetitivas de todos los genomas de entrada con Tantan @frith2011, un
paso recomendado por el pipeline de anotación para eucariotas del NCBI @ncbieuk.
Luego, los genomas enmascarados pasarán por AUGUSTUS @stanke2003, un programa
que identifica los genes presentes en los genomas, utilizando un modelo pre-
entrenado para _Fusarium_ que posee el programa. Los genes identificados serán
pasados a antiSMASH @blin2021 para la predicción de los BGCs, que luego serán
agrupados en GCFs con BiG-SCAPE @navarro2020. Usando GCFs selectas, se van a
resumir las diferencias principales entre los dos pares de genomas de interés.
Asimismo, los genes encontrados por AUGUSTUS serán la entrada para OrthoFinder
@emms2019, con el cual se podrá reconstruir los árboles filogenéticos con los
genomas completos para verificar la filogenia obtenida con el ITS y la
ß-tubulina, y comparar los genes presentes en cada par de genomas.

Los datos de entrenamiento para los modelos de predicción se construirán a
partir de todos los genomas disponibles de _F. oxysporum_ que tengan la etiqueta
de su _forma specialis_. Sobre estos genomas, se repetirá el proceso explicado
en la sección anterior de la metodología: se enmascaran las secuencias
repetitivas, se identifican los genes, se agrupan los genes en BGCs, y
finalmente se calculan las GCFs. Para un GCF dado, se tomarán las proteínas para
las cuales codifican los genes de sus BGCs y se pasarán como entrada a
GET\_HOMOLOGUES @contreras2013, un programa de análisis de pangenómica que
agrupará a las proteínas por similitud y función, obteniéndose el panclúster del
GCF en cuestión. Después de repetir este proceso para cada GCF, se construirá
una tabla donde cada fila es una cepa y cada columna será un gen de un BGC
perteneciente a una GCF. La tabla contendrá números enteros no negativos, donde
un cero representará ausencia de un gen dado, y cualquier otro número muestra el
número de copias de dicho gen. Además de esto, se ejecutará GET\_HOMOLOGUES
sobre el conjunto de proteínas completo, con el fin de obtener el pangenoma de
_F. oxysporum_. La tabla resultante del pangenoma será empleada como control: si
seleccionamos familias génicas aleatorias del pangenoma y el desempeño de los
modelos entrenados sobre estas familias es, en promedio, menor que el de los
panclústeres, podemos concluir que el metabolismo especializado es relevante
para la diferenciación entre las _formae speciales_ de _F. oxysporum_.

El diseño del modelo de predicción será realizado con el lenguaje de
programación de Python @vanrossum2009. Entre los análisis que se plantean, está
la aplicación de técnicas de reducción de dimensiones, tales como UMAP, PCA y
factorización de matrices no negativas, para su posterior exploración visual,
coloreando cada cepa con el color correspondiente a una _forma specialis_. Otra
técnica no supervisada será la selección de variables, en la cual se buscará
encontrar los genes que mejor explican la diferencia entre las _formae
speciales_. Para la construcción del modelo de predicción, se utilizará la tabla
de conteos como los atributos y las _formae speciales_ como las etiquetas
categóricas a predecir. Se probarán varios modelos supervisados tanto sobre la
tabla completa como sobre las tablas reducidas por reducción o selección de
variables y se evaluarán con métricas específicas para problemas de
clasificación multiclase.

= Cronograma y plan de trabajo

El plan preliminar para la composición de la tesis involucra ocho capítulos
(@chronogram), cada uno con una extensión mínima de 12 páginas. Los primeros dos
capítulos introducirán el problema a resolver y los conceptos más importantes de
la genómica a manera de un marco teórico. En los capítulos 3 a 7 se discutirán
los algoritmos, la metodología y los resultados de las diferentes fases del
proyecto de investigación. El último capítulo será designado para la discusión
general y conclusiones de los resultados del proyecto, así como potenciales
trabajos futuros. Los procedimientos que se discutirán en los capítulos 3 a 5 ya
están terminados. A partir del mes de diciembre, se estará trabajando en el
análisis que será descrito en los capítulos 6 y 7\. Los títulos de los capítulos
son tentativos.

#figure(
  table(
    columns: 3,
    align: left,
    stroke: none,
    table.header([*Mes*], [*Escritura de capítulos*], [*Análisis y entregas*]),
    table.hline(),
    [Dic 2024],
    [3: reconstrucción de genomas eucariotas],
    [Comparación de las cepas mexicanas con genomas de referencia],
    [Ene 2025],
    [4: identificación y agrupación de BGCs en  hongos ],
    [Aplicación de modelos de reducción de dimensiones],
    [Feb 2025],
    [5: pangenomas y panclústeres],
    [Diseño y evaluación de modelos de predicción],
    [Mar 2025],
    [6: selección de variables ],
    [Investigación bibliográfica de BGCs relevantes],
    [Abr 2025],
    [7: diseño y evaluación de modelos de predicción],
    [],
    [May 2025],
    [1: introducción y planteamiento del problema],
    [],
    [Jun 2025],
    [2: fundamentos de genómica],
    [],
    [Jul 2025],
    [8: conclusiones],
    [],
    [Ago 2025],
    [],
    [Revisión de texto por sínodo],
    [Sep 2025],
    [],
    [Aplicación de correcciones en tesis],
    [Oct 2025],
    [],
    [Entrega y defensa]
  ),
  caption: [Plan de trabajo por mes.]
) <chronogram>

#bibliography("ref.bib", style: "apa")
