# 扫雷数据

## 基础术语
rTime（real time）：也可直接称为time，即本局游戏从开始到结束用了多少时间。从第一次左击开始计时，到点到雷使得游戏失败，或者打开所有的非雷方块游戏胜利结束。精确到0.001秒。

Est Rtime（Estimated Real Time）：简写为estim或est。如果点到雷后游戏结束，假设接下来3BV/s不变，那么预计一共要用多少时间才能扫开本局。

sum：总和，指初级、中级、高级成绩相加而得出的总成绩。

sub：小于某数值，比如高级sub50就说明高级time <50.000s。

sup：大于某数值，比如高级3BV/s sup4就说明高级3BV/S≥4.000。

cell0~cell8：数字0的数量~数字8的数量。数字0在游戏局面上不显示。

mode：游戏模式，分为beg（初级8x8，10mines），int（中级16x16，40mines），exp（高级16x30，99mines），custom（自定义），cheat（作弊）等等。

## 操作术语
left：左击操作次数（不包括双击）。@之前为左击总次数，@之后为平均每秒左击次数。专业的扫雷软件在左键弹起时增加一个left。

right：右击操作次数（不包括双击）。@之前为右击总次数，@之后为平均每秒右击次数。专业的扫雷软件在右键按下时增加一个right。

flags：标雷的数量，先标雷后取消的不算。

double：双击操作次数。主要指左键、右键同时按下的操作，同时也指左键连按两次的操作。@之前为双击总次数，@之后为平均每秒双击次数。特殊情况：如果在已经打开的方格仅按下右键，那么记录一个right；如果在已经打开的方格上先按下右键，再按下左键形成double，那么记录一个double；如果在未被打开的方格上先按下右键，再按下左键形成double，那么记录一个right加一个double。

chording：双击，指左键、右键同时按下的操作。

cl（Click）：总操作次数，等于左键、右键、双击操作之和。@之前是总操作次数，@之后是平均每秒操作次数。

cl/s：简称cls，即平均每秒操作次数，包括左击、右击和双击。

ces（Effective Clicks）：简称ce，指能够推进局面、使局面发生实质性变化的操作数。根据evf标准（元扫雷所采用），具体包括：（1）左键打开一个非雷方块；（2）在周围已全部正确标雷的数字上面双击，以打开这个数字周围的所有非雷方块；（3）在是雷的方块上首次右击标雷。Ce不包括的情况：（1）在已经打开的数字或空上面左击；（2）在周围还未全部标雷的数字上双击，使这个数字周围的所有未开方块只是闪一下，并未被打开；（3）错误标雷（MISFLAGS），即在非雷格子上标雷；（4）取消标雷（UNFLAGS），指在非雷的格子却标雷的格子上右击以取消标雷；（5）错误的取消标雷（MISUNFLAGS），指在是雷的格子上标雷，并取消标雷。（6）在是雷的方块上非首次右键标雷。根据avf标准（arbiter所采用），在是雷的方块上无论第几次右键标雷，都算作ce。

Leff（Left-efficient Click/L-eff）：左键有效点击数。指使局面发生实质性、积极改变的左键点击数。

Reff（Right-efficient Click/R-eff）：右键有效点击数。指使局面发生实质性、积极改变的右键点击数。

Deff（Double-efficient Click/D-eff）：双键有效点击数。指使局面发生实质性、积极改变的双击数。

FL：标雷扫法。使用左键，并使用至少一次右键或双击解开局面的扫法。

NF（No Flag）：盲扫。只使用左键，不使用右键或双击解开局面的扫法。

Flags used：被用于双击开空的标雷数。

Unflags：取消标雷。

Waste flags：未被使用的标雷。

## 局面指标
ops（Openings）：简称op、空，局面中没有数字的格子即为数字0，数字0的八连通域个数称为空（的个数）。

isls（Islands）：简称is、岛，将局面中的空及其边缘、雷删除以后，其余部分的八连通域个数称为岛（的个数）。

3BV（Bechtel's Board Benchmark Value）：可进一步简称BV。3BV指仅使用左键解开当前局面，所需要的理论最少左击次数。3BV可以拆分为：所有岛上的格子总数+Op。该指标用来粗略估计一个局面难度的高低，一般BV越大，则解开局面所用的时间越长；3BV高的图，一般称为大图，向下依次称为中图、小图。此外，录像的3BV值还关系到其记录是否受到承认。为获得国内外各排行榜的承认，初级、中级、高级这三个难度的纪录录像的3BV分别需要大于等于2、30、100；而初级3BV/s纪录录像的3BV则需要大于等于10。局面的3BV值也用于计量当局游戏的完成度，当且仅当打开所有的3BV时，游戏获胜。

[3BVO](https://www.minesweeper.info/articles/3BV_Limits_On_Trial.pdf)：计算方法是3BV+2*(op-1)。

Solved 3BV：已经扫开的3BV，如果一个Op没有全部打开则不计入。

completion：局面完成度，计算方法是Solved 3BV/3BV，即已点开的3BV与总3BV之比。

ZiNi（ZiNi由来自德国下萨克森州希尔德斯海姆市的Elmar Zimmermann提出，由来自奥地利的Christoph Nikolaus加以补充并编程实现的，因此该指标的命名结合了他们的姓）：解开当前局面所需的理论最少操作次数，这里的操作包括左键、右键和双击。@之前为当前局面的总ZiNi数，@之后为平均每秒玩家能解开的ZiNi个数。与计算3BV不同，计算ZiNi是NP难题，目前主流专业扫雷软件均采用估算。ZiNi 的三种算法：贪婪算法（Greedy ZiNi）、仿人类算法（Human ZiNi）和随机算法（Random ZiNi）。G. ZiNi可以简写为ZiNi。

H. ZiNi（Human ZiNi）：仿人类算法的ZiNi。

G. ZiNi（Greedy ZiNi）：贪婪算法的ZiNi。通常有H. ZiNi>G. ZiNi。

R. ZiNi（Random ZiNi）：随机算法的ZiNi。

8-Way ZiNi：包含Greedy 8-Way ZiNi和Human 8-Way ZiNi。G. ZiNi和H. ZiNi算法如果局面旋转90度，就可能计算出来的ZiNi值不同。因此考虑将局面旋转90度旋转4次，再镜像后旋转90度旋转4次，选取8次计算结果的最小值。

[Pttazini（PTTACGfans's ZiNi）](https://github.com/PTTACGfans/Minesweeper-ZiNi-Calculator)：目前为止最少点击次数方面最好的结果。使用了“左键点开改为双键点开”、“左键点开改为点空点开”、“移除不必要的候选项”、“调整特定格子的优先度”等改进。

## 基本实力指标
3BV/s：简称3BVS，亦可进一步简称为BVS。3BV/s=3BV/ RTime。代表每秒能解决几个3BV，是衡量扫雷速度的重要指标，是除时间外另一个设立世界纪录的指标。

Corr（Correctness）：有效点击效率，计算公式Ce/Cl。也就是在全部操作中，实际推进局面的操作的占比。反映了点击的准确率。

ThrP（ThroughPut）：有效操作效率，计算公式3BV/Ce。即去除废操以后，平均每个有效操作能够解决几个3BV。在NF中，能否点出关键op对于thrp产生决定性影响，因此也称为破空率。

IOE（Index of Efficiency）：效率指标，计算公式3BV/CL，即Corr×ThrP。平均每个操作能够解决几个3BV，反映了玩家的总体解开局面的效率。

ZNE（ZiNi Efficiency）：计算公式ZiNi/Cl。在NF扫法下无意义，在标雷局反映标雷模式的操作效率。

HZNE：计算公式H. ZiNi/Cl。

ZNT（ZiNi ThroughPut）：计算公式ZiNi/Ce。

HZNT：计算公式H. ZiNi/Ce。

path/Distance/路程/距离：鼠标移动路线的长度，单位为像素（pixel），局面中每一个方块的边长称为一个格子距离（square-path）。早期扫雷的格子的边长为16像素，此后不论实际边长为多少像素，统一归一化为16像素。

CPath（click path）：每两次点击位置之间的距离之和，单位为像素（pixel）。

## 复杂实力指标
RQP（Rapport Qualité Prix）：计算公式$\frac{(rTime+1)rTime}{Solved\ 3BV}$，即$\frac{rTime+1}{Solved\ 3BV/s}$，越小越好。

QG（Quality Grade）：计算公式为$\frac{rTime^{1.7} }{Solved\ 3BV}$，越小越好。

STNB（尸体牛逼）：由郭锦洋提出，旧版的计算公式：初级为$\frac{47.299*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$；中级为$\frac{153.73*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$；高级为$\frac{435.001*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$。新版的计算公式：初级为$\frac{36*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$；中级为$\frac{162*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$；高级为$\frac{435*Solved\ 3BV}{rTime^{1.7} }*\sqrt{\frac{Solved\ 3BV}{3BV} }$，越大越好。

IODE（index of distance efficiency）：距离效率指标，计算公式$\frac{Solved\ 3BV}{path/16}$。反映规划能力和手稳程度。

IOPE（index of path efficiency）：路程效率指标，计算公式$\frac{CPath}{path}$。反映手稳程度。

Move：指MoveSpeed，鼠标指针在图上移动的速度，简称移速，单位是pixel/s，像素每秒。计算公式$\frac{path}{time}$。

IOS（Index of Speed）：已废弃。速度指标，计算公式$\frac{\log_{10}{Solved\ 3BV} }{\log_{10}{rTime} }$，越小越好。

OBV（Schu's Optimized Board Value）：已废弃。计算公式初级为0.07×numbers+0.43×3BV+ 2.27×Op；中级为0.20×numbers+0.32×3BV+1.38×Op；高级为0.38×numbers+0.23×3BV+0.99×Op。其中numbers = (cell1 + cell2 + cell3 + cell4 + cell5 + cell6 + cell7 + cell8 - 124)。

pLuck：由濮天翌提出，以对数概率的相反数衡量的后验开率。计算方法每次猜雷正确的概率p，对数概率的相反数为-log10(p)，将其累加得到pLuck。

## 统计指标
Ranks：简称RANK，一个局面彻底完成时才会给出该指标。写法为：【当前级别当前扫法（FL or NF）之下的时间排名】 / 【当前级别当前扫法之下的3BV/s排名】 of 【当前级别已完成总局数】。比如，完成的某一局高级盲扫，在玩家个人历史高级盲扫时间的排名是第17、BVS排名第30，且玩家总共完成了500局高级，那么RANK就是17/30 of 500。

ios rank：IOS的排名，写法同RANK。

rqp rank：RQP的排名，写法同RANK。

pb（Personal best）：指每个难度级别的各个bv的局面的个人最好成绩。

Hopsing：指同时创造个人的Time和3BV/s记录，即双破。

## 其他术语
1.5 Click：一种技巧。指右键按下标雷（不弹起），接着移动鼠标到目标数字，同时按下左键，最后左键和右键同时在目标数字上弹起完成双击。

completion：局面完成度，计算方法是Solved 3BV/3BV，即已点开的3BV与总3BV之比。

UPK（Unfair Prior Knowledge）：指重新开始同一局面的游戏模式。由于这样做用到了不公平的先验知识，因此属于作弊模式。

Board Cycles：局面循环。由于伪随机数生成算法存在缺陷，Windows XP自带扫雷存在的循环重复出现同一个局面，及其经过平移、旋转得到的局面的Bug。

dreamboard：梦幻图。泛指3BV小，猜雷少的好图。此外特指历史上一个著名的存在局面循环的中级局面，有玩家找到规律并在此局面下通过UPK取得惊人成绩。

minute barrier：分障。常有玩家在60s大关受阻很久，特别指Time突破60s时遇到的瓶颈。

Elmar's Syndrome：艾尔玛综合征。指连续取得且长期未能突破同一成绩（精确到秒）的现象。

MB（Miss Block）：整个局面都完成，但有一个方块因忽视而没有点开的情况。

LC（Lose on the last click）：打开最后一个方格时不幸踩雷。

## 中文术语
破空：一种解局的方法论。指试图通过猜测，预判出空的可能的位置，提前打开该位置，以减少在空的边缘的点击次数。

翻墙：一种解局的方法论。指试图点击成排的雷背后的区域，以降低解局难度、打破僵局。

飞标：FL扫法的旧称。

跳判：一种解局的方法论。指判雷顺序与操作处理顺序不相同的解局过程。具体指：在利用可以判雷的最小局部进行第一次判雷后，暂时不进行操作处理，而是依靠该判雷结果继续进行后续的判雷；在操作时，先对后续判雷结果操作处理，再对之前的判雷结果操作处理；以此来优化鼠标移动路径、提高操作流畅度的方法。

全标：标雷数量较多的扫法。通常高级标雷数量超过80就可以被称为全标扫法。

尸体：指扫到一半由于点到雷游戏结束，然后保存的录像。

欠债：指玩家的高级Time按整数计时头部成绩出现断层的情况。例如：玩家的高级Time分别是41.35（42）、44.21（45）、44.78（45）、45.39（46）、46.28（47），这个时候就可以说这位玩家欠债了，他欠了43、44。

还债：上面这位玩家，假设他又继续扫出了一局42.77（43）那么这个时候就可以说他把43秒给还上了，这叫还债。

梁山分（lsf）：梁山分是一种根据全国顶尖玩家的数据，动态评估一名玩家水平的评分。综合了玩家三级别（其中初级要求bv≥10）time、bvs、STNB三项参数以及前五局的平均成绩，计算公式为：lsf=0.94×软实力+0.06×NF软实力；其中软实力=5×初级软实力+12×中级软实力+16×高级软实力；其中各级别的软实力是该级别三参数软实力的加权平均，具体权值如下：

| 级别  | time  | bvs    |  STNB  |
| ---- | ----  | ----  | ----  |
| 初级 | 31% |   44%    |  25%    |
| 中级 | 34% |   34%    |  32%    |
| 高级 | 33% |   33%    |  34%    |

其中各级别各参数软实力的计算方法为，以100为基准值，达到100相当于水平达到了NT20.5的水准；其中NT20.5表示全国.5前20人的对应指标的平均值；其中.5表示各级别各参数生涯最好成绩的平均值。




