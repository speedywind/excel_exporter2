# Excel exporter

## commit_excel.bat
将NAS中的excel直接拖拽到此脚本上进行提交实现自动提交

## Example

excel 导出 lua 表   
支持类型: int,bool,float,string,struct<int>,struct<bool>,list<struct>   
特别说明default(仅用于struct): list<struct<int:itemid,default:count=1>>:reward   
特别说明: IsMyInt0 IsMyInt IsMyString中的字段可以不配类型   
特别说明<(<数相同表示同级元素): list<struct<int:hpbar>>:enemy	<list<struct<int:enemyid>>:enemy	string:enemyname	int:count=1	int:lv=0   
导出结构示例: ld_enemy:id=key  name  struct<int:itemid>:cost  struct<int:hpbar=1>:enemygroup  <list<struct<int:itemid>>:lootlist  count  <list<struct<int:id>>:enemy  <<list<struct<int:enemylv=0>>:enemylv

```txt
 ld_enemy    (源自ld_enemy:id=key  name)
 ├──[1]={id = 1, name = "enemy1",
 │   ├──cost={itemid = 1001, count = 1},     (源自struct<int:itemid,default:count=1>:cost)
 │   └──enemygroup={hpbar = 2,    (源自struct<int:hpbar=1>:enemygroup)
 │          ├──lootlist={         (源自<list<struct<int:itemid>>:lootlist  count)
 │          │      ├──{itemid = 1001, count = 10},
 │          │      └──{itemid = 1002, count = 100}},
 │          │
 │          └──enemy={            (源自<list<struct<int:id>>:enemy  <<list<struct<int:enemylv=0>>:enemylv)
 │               ├──{id = 40012,
 │               │  └──enemylv={{enemylv = -1}}},
 │               ├──{id = 40013,
 │               │  └──enemylv={{enemylv = 0}}},
 │               └──{id = 40014,
 │                  └──enemylv={{enemylv = 1}}}}}},
 └──[2]={id = 2, name = "enemy2",
     ├──cost={itemid = 1001, count = 1},
     └──enemygroup={hpbar = 2,
            ├──lootlist={
            │      ├──{itemid = 1001, count = 10},
            │      └──{itemid = 1002, count = 100}},
            │
            └──enemy={
                 ├──{id = 40012,
                 │  └──enemylv={{enemylv = -1}}},
                 ├──{id = 40013,
                 │  └──enemylv={{enemylv = 0}}},
                 └──{id = 40014,
                    └──enemylv={{enemylv = 1}}}}}},
```