# Enka.Network - API

## Содержание

- [Начало работы](#начало-работы)
- [Структура данных](#структура-данных)
- [Определения](#определения)
- [Иконки и изображения](#иконки-и-изображения)
- [Локализация](#локализация)

## Начало работы

Вы можете использовать API напрямую, либо использовать библиотеки-врапперы, написанные другими. API довольно несложное, основная работа заключается в поиске нужных вещей в датамайне из игры на основе данных, которые возвращает API - в этом основной функционал такой библиотеки.

В разделе [библиотеки-врапперы](#библиотеки-врапперы) вы можете найти библиотеку на подходящем языке программирования.

## То, чего следует придерживаться при запросах

Несколько правил использования API:

1. Пожалуйста, не пытайтесь перебирать UID или выполнять массовые запросы (чтобы разом заполнить свою базу данных, например). В игре сотни миллионов UID, через мой API это просто не представляется вомзожным. Возможно, позднее я сделаю выгрузку, которую можно будет скачать целиком.

2. Поставьте `User-Agent` хедер на ваши запросы, чтобы я мог их видеть - для того чтобы я если что смог помочь или подсказать что-то.

3. На запрос данных по UID есть динамические рейтлимиты — если вы делаете слишком много запросов, время отклика будет расти. В конце концов вы уткнетесь в HTTP-код 429. В этом случае нужно принять меры, чтобы уменьшить их количество. Можете связаться со мной, чтобы узнать, возможно ли увеличить рейтлимиты для вашего конкретного случая, но в большинстве случаев это не нужно и просто является результатом неоптимизированного кода.

4. Запросы на UID возвращают поле `ttl` - это поле означает "сколько осталось секунд до очередного запроса в игру". Пока `ttl` не истечет, эндпоинт будет возвращать кешированные данные - но в рейтлимит такой запрос всё равно будет считаться. Рекоменндую кэшировать данные и использовать `ttl` для того, чтобы UID нельзя было запросить снова (пока оно не истечет). Для этого рекомендую использовать Redis.

Если есть вопросы по API или распарсиванию данных, можете задать вопрос на [Discord-сервере](https://discord.gg/PcSZr5sbn3).

## API

### UID-эндпоинты

#### Получение данных с витрины с полной информацией об игроке

> https://enka.network/api/uid/618285856/

Ответ будет содержать `playerInfo` и `avatarInfoList`. `playerInfo` содержит основные данные об игровом аккаунте. Если `avatarInfoList` отсутствует, это значит, что витрина этой учетной записи либо скрыта игроком, либо там нет персонажей.

#### Получение только информации об игроке

> https://enka.network/api/uid/618285856/?info

Подставив `?info` к запросу, Вы получите только `playerInfo`. Основной эндпоинт всегда дополнительно делает запрос для получения `avatarInfoList`; если Вам нужен только `playerInfo`, используйте `?info` - он работает быстрее и на нём меньше рейтлимиты.

Кроме того, оба ответа будут содержать объект «владелец» (`owner`), если:

1. У пользователя есть аккаунт на сайте;
2. Пользователь добавил свой UID в профиль;
3. Пользователь верицифировал, что UID принадлежит ему;
4. Пользователь установил его видимость на «публичный».

Подробнее об учетных записях пользователей ниже.

#### Коды ответов HTTP

Убедитесь, что Вы правильно обрабатываете их в своем приложении.

```
400 = Неверный формат UID
404 = Игрок не существует (так сказали сервера михоёв, не стоит на это 100% полагаться)
424 = Обслуживание серверов / все сломалось после обновления
429 = Ограничена скорость (либо моим сервером, либо сервером михоёв)
500 = Общая ошибка сервера (что-то не так в данных?)
503 = Всё умерло насмерть
```

### Эндпоинты профиля

На сайте можно создать аккаунт (профиль) и привязать к нему несколько игровых аккаунтов. Затем, с помощью кода подтверждения, засунутого в подпись, пользователи могут подтвердить, что это их аккаунт — таким образом сайт можем гарантировать, что игровой аккаунт принадлежит данному человеку.

Пользователи могут сохранять снапшоты сборок под произвольными именами, я их называю «сохраненные сборки».

> https://enka.network/api/profile/Algoinde/

Получает информацию о пользователе

> https://enka.network/api/profile/Algoinde/hoyos/

Получает список «hoyos» — учетные записи в Геншине и метаданные о них. Эндпоинт вернет только те учетные записи, которые являются и `verified`, и `public` (пользователи могут скрывать учетные записи; неподтвержденные учетные записи скрыты по умолчанию). Каждый ключ в ответе является уникальным идентификатором для `hoyo` - его затем можно использовать для последующих запросов, чтобы получить информацию о персонажах/сборках этого игрового аккаунта.

> https://enka.network/api/profile/Algoinde/hoyos/4Wjv2e/

Возвращает метаданные для одного hoyo (игрового аккаунта).

> https://enka.network/api/profile/Algoinde/hoyos/4Wjv2e/builds/

Возвращает сохраненные сборки для данного hoyo. Это объект массивов, где ключом является `avatarId` персонажа, а объекты в массивах — разные сборки для данного персонажа в произвольном порядке (однако, у них есть поле `order`, по которому можно их упорядочить для отображения).

Если в сборке есть поле `live: true`, это значит, что это не «сохраненная» сборка, а та, что была получена из витрины, когда была нажата кнопка «обновить». При обновлении все старые `live` сборки удаляются и создаются новые. Только пользователь решает, когда выполнять это обновление — эти данные НЕ будут актуальными.

Как указано в разделе [UID-эндпоинты](#uid-эндпоинты), при запросе UID в ответе может быть объект `owner`. Используя поля в этом объекте, можно сконструировать API-ссылку на профиль:

`https://enka.network/api/profile/{owner.username}/hoyos/{owner.hash}/builds/`

## Структура данных

| Название | Описание |
| :--- | :---------- |
| [playerInfo](#playerinfo) | Информация профиля |
| [avatarInfoList](#avatarinfolist) | Список подробной информации по каждому персонажу из витрины |

### playerInfo

Базовые данные персонажей по ID можно получить из [store/characters.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/characters.json).  <br />
Для дополнительной информации можно обратиться к [данным персонажей](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/AvatarExcelConfigData.json).

| Название | Описание |
| :--- | :--------- |
| nickname | Никнейм игрока |
| signature | Подпись ппрофиля |
| worldLevel | Уровень мира игрока |
| namecardId | ID именной карточки профиля |
| finishAchievementNum | Количество полученных достижений |
| towerFloorIndex | Этаж бездны |
| towerLevelIndex | Комната бездны |
| [showAvatarInfoList](#showavatarinfolist) | Список ID персонажей и уровней |
| showNameCardIdList | Список ID именных карточек |
| profilePicture.avatarId | ID персонажа на аватарке |

#### showAvatarInfoList

| Название | Описание |
| :--- | :--------- |
| avatarId | ID персонажа |
| level | Уровень персонажа |
| costumeId | ID скина персонажа. Смотрите `"costumes"` в [store/characters.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/characters.json) |

### avatarInfoList

Базовые данные персонажей по ID можно получить из [store/characters.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/characters.json).  <br />
Для дополнительной информации можно обратиться к [данным персонажей](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/AvatarExcelConfigData.json).

| Название | Описание |
| :--- | :---------- |
| avatarID | ID персонажа |
| talentIdList | Список ID созвездий <br /> Нет данных, если 0 созвездий |
| [propMap](#propmap) | Список свойств информации о персонаже |
| fightPropMap -> `{id: value}` |  `Map` боевых свойств персонажа. <br />Смотрите [определения для ID](#fightprop)|
| skillDepotId | ID набора навыков персонажа <br />[Данные умений](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/AvatarSkillDepotExcelConfigData.json) ->     `"id"`|
| inherentProudSkillList | Список разблокированных ID навыков <br />[Данные умений](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/AvatarSkillDepotExcelConfigData.json) -> `"inherentProudSkillOpens"` |
| skillLevelMap -> `{skill_id: level}`| `Map` уровней навыков <br /> [Данные умений](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/AvatarSkillDepotExcelConfigData.json) -> `"inherentProudSkillOpens"` |
| [equipList](#equiplist) | Список снаряжения: Оружие, Артефакты |
| fetterInfo.expLevel  | Уровень дружбы персонажа |

#### propMap

| Название | Описание |
| :--- | :--------- |
| type | ID статы, см. [определения для ID статов](#prop) |
| ival | На это можно забить |
| val  | Значение этой статы |

#### equipList

| Название | Описание |
| :--- | :--------- |
| itemId | ID оружия <br /> [Данные артефактов](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/ReliquaryExcelConfigData.json) -> `"id"` <br /> [Данные оружия](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/WeaponExcelConfigData.json) -> `"id"` |
| [weapon](#weapon) `[Только оружие]` | Базовая информация об оружии  |
| [reliquary](#reliquary) `[Только артефакт]` | Базовая информация об артефакте  |
| [flat](#flat) | Дополнительная распарсенная информация |

#### weapon

Для получения дополнительной информации об оружии можно обратиться к [данным оружий](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/WeaponExcelConfigData.json)

| Название | Описание |
| :--- | :---------- |
| level | Уровень оружия |
| promoteLevel | Уровень возвышения оружия |
| affixMap | Уровень пробуждения оружия `[0-4]` |

#### reliquary

Для получения дополнительной информации об артефактах можно обратиться к [данным артефактов](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/ReliquaryExcelConfigData.json)

| Название | Описание |
| :--- | :---------- |
| level | Уровень артефакта `[1-21]` |
| mainPropId | ID основного стата артефакта <br /> [Данные основных статов](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/ReliquaryMainPropExcelConfigData.json) |
| appendPropIdList | Список ID подстатов артефакта <br /> [Данные подстатов](https://gitlab.com/Dimbreath/AnimeGameData/-/blob/master/ExcelBinOutput/ReliquaryAffixExcelConfigData.json) |

#### flat

| Название | Описание |
| :--- | :---------- |
| nameTextHashMap | Хэш имени предмета <br /> См. [локализация](#локализация) |
| setNameTextHashMap `[Только артефакт]`| Хэш для названия сета артефактов <br /> См. [локализация](#локализация)|
| rankLevel | Уровень редкости снаряжения |
| [reliquaryMainstat](#reliquarymainstat-reliquarysubstats-weaponstats) `[Только артефакт]` | Основной стат артефакта |
| [reliquarySubstats](#reliquarymainstat-reliquarysubstats-weaponstats) `[Только артефакт]` | Список подстатов артефакта |
| [weaponStats](#reliquarymainstat-reliquarysubstats-weaponstats) `[Только оружие]`| Список статов оружия: Базовая слиа атаки, подстат |
| [itemType](#itemtype) | Тип снаряжения: оружие или артефакт |
| icon | Название иконки снаряжения <br /> [Использование названий иконок](#иконки-и-изображения)|
| [equipType](#equiptype) `[Только артефакт]` | Тип артефакта |

#### reliquaryMainstat, reliquarySubstats, weaponStats

| Название | Описание |
| :--- | :---------- |
| mainPropId / appendPropID | ID статы снаряжения. Смотрите [определения имён](#appendprop)|
| propValue | Значение статы |

## Определения

### Prop

| Тип | Описание |
| :--: | :---------- |
| 1001 | Опыт |
| 1002 | Возвышение |
| 4001 | Уровень |

### FightProp

| Тип | Описание |
| :--: | :---------- |
| 1 | Базовое HP |
| 2 | HP |
| 3 | HP% |
| 4 | Базовая сила атаки |
| 5 | Сила атаки |
| 6 | Сила атаки % |
| 7 | Базовая защита |
| 8 | Защита |
| 9 | Защита % |
| 10 | Базовая скорость атаки |
| 11 | Скорость атаки % |
| 20 | Шанс крит. попадания |
| 22 | Крит. урон |
| 23 | Восст. энергии |
| 26 | Бонус лечения |
| 27 | Бонус получаемого лечения |
| 28 | Мастерство стихий |
| 29 | Физ. сопротиление |
| 30 | Бонус физ. урона |
| 40 | Бонус Пиро урона |
| 41 | Бонус Электро урона |
| 42 | Бонус Гидро урона |
| 43 | Бонус Дендро урона |
| 44 | Бонус Анемо урона |
| 45 | Бонус Гео урона |
| 46 | Бонус Крио урона |
| 50 | Пиро сопротивление |
| 51 | Электро сопротивление |
| 52 | Гидро сопротивление |
| 53 | Дендро сопротивление |
| 54 | Анемо сопротивление |
| 55 | Гео сопротивление |
| 56 | Крио сопротивление |
| 70 | Потребление Пиро энергии |
| 71 | Потребление Электро энергии |
| 72 | Потребление Гидро энергии |
| 73 | Потребление Дендро энергии |
| 74 | Потребление Анемо энергии |
| 75 | Потребление Крио энергии |
| 76 | Потребление Гео энергии |
| 80 | Снижение времени отката |
| 81 | Прочность щита |
| 1000 | Текущая Пиро энергия |
| 1001 | Текущая Электро энергия |
| 1002 | Текущая Гидро энергия |
| 1003 | Текущая Дендро энергия |
| 1004 | Текущая Анемо энергия |
| 1005 | Текущая Крио энергия |
| 1006 | Текущая Гео энергия |
| 1010 | Текущее HP |
| 2000 | Максимальное HP |
| 2001 | Сила атаки |
| 2002 | Защита |
| 2003 | Скорость атаки |
| 3025 | Крит. шанс элементальной реакции |
| 3026 | Крит. урон элементальной реакции |
| 3027 | Крит. шанс элементальной реакции (Перегрузка) |
| 3028 | Крит. урон элементальной реакции (Перегрузка) |
| 3029 | Крит. шанс элементальной реакции (Рассеивание) |
| 3030 | Крит. урон элементальной реакции (Рассеивание) |
| 3031 | Крит. шанс элементальной реакции (Заряжен) |
| 3032 | Крит. урон элементальной реакции (Заряжен) |
| 3033 | Крит. шанс элементальной реакции (Сверхпроводник) |
| 3034 | Крит. урон элементальной реакции (Сверхпроводник) |
| 3035 | Крит. шанс элементальной реакции (Горение) |
| 3036 | Крит. урон элементальной реакции (Горение) |
| 3037 | Крит. шанс элементальной реакции (Заморозка (Разбит)) |
| 3038 | Крит. урон элементальной реакции (Заморозка (Разбит)) |
| 3039 | Крит. шанс элементальной реакции (Бутонизация) |
| 3040 | Крит. урон элементальной реакции (Бутонизация) |
| 3041 | Крит. шанс элементальной реакции (Цве­тение) |
| 3042 | Крит. урон элементальной реакции (Цве­тение) |
| 3043 | Крит. шанс элементальной реакции (Веге­тация) |
| 3044 | Крит. урон элементальной реакции (Веге­тация) |
| 3045 | Базовый крит. шанс элементальной реакции |
| 3046 | Базовый крит. урон элементальной реакции |

### ItemType

| Название | Описание |
| :--- | :---------- |
| ITEM_WEAPON | Оружие |
| ITEM_RELIQUARY | Артефакт |

### EquipType

| Название | Описание |
| :--- | :---------- |
| EQUIP_BRACER | Цветок жизни |
| EQUIP_NECKLACE | Перо смерти |
| EQUIP_SHOES | Пески времени |
| EQUIP_RING | Кубок пространства |
| EQUIP_DRESS | Корона разума |

### AppendProp

| Название | Описание |
| :--- | :---------- |
| FIGHT_PROP_BASE_ATTACK `[Оружие]` | Базовая сила атаки |
| FIGHT_PROP_HP | Целочисленное HP |
| FIGHT_PROP_ATTACK | Целочисленная сила атаки |
| FIGHT_PROP_DEFENSE | Целочисленная защита |
| FIGHT_PROP_HP_PERCENT | HP% |
| FIGHT_PROP_ATTACK_PERCENT | Сила атаки % |
| FIGHT_PROP_DEFENSE_PERCENT | Защита % |
| FIGHT_PROP_CRITICAL | Шанс крит. попадания |
| FIGHT_PROP_CRITICAL_HURT | Крит. урон |
| FIGHT_PROP_CHARGE_EFFICIENCY | Восст. энергии |
| FIGHT_PROP_HEAL_ADD | Бонус лечения |
| FIGHT_PROP_ELEMENT_MASTERY | Мастерсто стихий |
| FIGHT_PROP_PHYSICAL_ADD_HURT | Бонус физ. урона |
| FIGHT_PROP_FIRE_ADD_HURT | Бонус Пиро урона |
| FIGHT_PROP_ELEC_ADD_HURT | Бонус Электро урона |
| FIGHT_PROP_WATER_ADD_HURT | Бонус Гидро урона |
| FIGHT_PROP_WIND_ADD_HURT | Бонус Анемо урона |
| FIGHT_PROP_ICE_ADD_HURT |  Бонус Крио урона |
| FIGHT_PROP_ROCK_ADD_HURT | Бонус Гео урона |
| FIGHT_PROP_GRASS_ADD_HURT | Бонус Дендро урона |

## Иконки и изображения

Иконки персонажей, оружия и артефактов можно взять с моего CDN, по URL `https://enka.network/ui/[icon_name].png`.  
Обычно название иконки начинается с `"UI_"` или `"Skill_"` для [талантов персонажей](#персонажи-таланты-и-созвездия).  
Например, https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png.

### Оружия и артефакты

Внутри объектов [flat](#flat) есть `icon`.

### Персонажи, таланты и созвездия

В [store/characters.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/characters.json) - строки, которые «UI_XXXXXX» или «Skill_XXXXXX» - находятся по ID персонажа.

## Локализация

`"NameTextMapHash"` в [store/characters.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/characters.json), `"nameTextHashMap"` и `"setNameTextHashMap"` в [flat](#flat) используется в качестве ключа для получения локализованных названий предметов из [store/loc.json](https://github.com/EnkaNetwork/API-docs/blob/master/store/loc.json).  
Также можно взять локализацию для [AppendProp](#appendprop) используя имя свойства в качестве ключа - `"FIGHT_PROP_HP"`, `"FIGHT_PROP_HEAL_ADD"` и так далее.

Дополнительные локализованные строки можно взять из [TextMap Data](https://gitlab.com/Dimbreath/AnimeGameData/-/tree/master/TextMap) (включает только языки, поддерживаемые игрой).

## Библиотеки-врапперы

TS/JS - https://www.npmjs.com/package/enkanetwork.js - [Jelosus1](https://github.com/Jelosus2)

TS/JS - https://github.com/yuko1101/enka-network-api - [yuko1101](https://github.com/yuko1101)

Rust - https://github.com/eratou/enkanetwork-rs - [eratou](https://github.com/eratou)

Python - https://github.com/mrwan200/enkanetwork.py - [mrwan200](https://github.com/mrwan200)