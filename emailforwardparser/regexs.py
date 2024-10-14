import re

MAILBOX_SEPARATORS = [",", ";"]

# Compile regex patterns
QUOTE_LINE_BREAK_OPTIONAL = re.compile(r"(?m)^(>+)=20?$")
QUOTE_LINE_BREAK = re.compile(r"(?m)^(>+)\s?$")
QUOTE = re.compile(r"(?m)^(>+)\s?")
FOUR_SPACES = re.compile(r"(?m)^(\ {4})\s?")
CARRIAGE_RETURN = re.compile(r"(?m)\r\n")
BYTE_ORDER_MARK = re.compile(r"(?m)\xFEFF")
TRAILING_NON_BREAKING_SPACE = re.compile(r"(?m)\xA0$")
NON_BREAKING_SPACE = re.compile(r"(?m)\xA0")

SUBJECT = [
    # Outlook Live / 365 (cs, en, hr, hu, sk), Yahoo Mail (all locales)
    re.compile(r"(?m)^Fw:(.*)"),
    # Outlook Live / 365 (da), New Outlook 2019 (da)
    re.compile(r"(?m)^VS:(.*)"),
    # Outlook Live / 365 (de), New Outlook 2019 (de)
    re.compile(r"(?m)^WG:(.*)"),
    # Outlook Live / 365 (es), New Outlook 2019 (es)
    re.compile(r"(?m)^RV:(.*)"),
    # Outlook Live / 365 (fr), New Outlook 2019 (fr)
    re.compile(r"(?m)^TR:(.*)"),
    # Outlook Live / 365 (it), New Outlook 2019 (it)
    re.compile(r"(?m)^I:(.*)"),
    # Outlook Live / 365 (nl, pt), New Outlook 2019 (cs, en, hu, nl, pt, ru, sk), Outlook 2019 (all locales)
    re.compile(r"(?m)^FW:(.*)"),
    # Outlook Live / 365 (no)
    re.compile(r"(?m)^Vs:(.*)"),
    # Outlook Live / 365 (pl), New Outlook 2019 (pl)
    re.compile(r"(?m)^PD:(.*)"),
    # Outlook Live / 365 (pt-br), New Outlook 2019 (pt-br)
    re.compile(r"(?m)^ENC:(.*)"),
    # Outlook Live / 365 (ro)
    re.compile(r"(?m)^Redir.:(.*)"),
    # Outlook Live / 365 (sv), New Outlook 2019 (sv)
    re.compile(r"(?m)^VB:(.*)"),
    # New Outlook 2019 (fi)
    re.compile(r"(?m)^VL:(.*)"),
    # New Outlook 2019 (no)
    re.compile(r"(?m)^Videresend:(.*)"),
    # New Outlook 2019 (tr)
    re.compile(r"(?m)^İLT:(.*)"),
    # Gmail (all locales), Thunderbird (all locales), Missive (en)
    re.compile(r"(?m)^Fwd:(.*)"),
]

SEPARATOR = [
    # Apple Mail (en)
    re.compile(r"^>?\s*Begin forwarded message\s?:"),
    # Apple Mail (cs)
    re.compile(r"(?m)^>?\s*Začátek přeposílané zprávy\s?:"),
    # Apple Mail (da)
    re.compile(r"(?m)^>?\s*Start på videresendt besked\s?:"),
    # Apple Mail (de)
    re.compile(r"(?m)^>?\s*Anfang der weitergeleiteten Nachricht\s?:"),
    # Apple Mail (es)
    re.compile(r"(?m)^>?\s*Inicio del mensaje reenviado\s?:"),
    # Apple Mail (fi)
    re.compile(r"(?m)^>?\s*Välitetty viesti alkaa\s?:"),
    # Apple Mail (fr)
    re.compile(r"(?m)^>?\s*Début du message réexpédié\s?:"),
    # Apple Mail iOS (fr)
    re.compile(r"(?m)^>?\s*Début du message transféré\s?:"),
    # Apple Mail (hr)
    re.compile(r"(?m)^>?\s*Započni proslijeđenu poruku\s?:"),
    # Apple Mail (hu)
    re.compile(r"(?m)^>?\s*Továbbított levél kezdete\s?:"),
    # Apple Mail (it)
    re.compile(r"(?m)^>?\s*Inizio messaggio inoltrato\s?:"),
    # Apple Mail (nl)
    re.compile(r"(?m)^>?\s*Begin doorgestuurd bericht\s?:"),
    # Apple Mail (no)
    re.compile(r"(?m)^>?\s*Videresendt melding\s?:"),
    # Apple Mail (pl)
    re.compile(r"(?m)^>?\s*Początek przekazywanej wiadomości\s?:"),
    # Apple Mail (pt)
    re.compile(r"(?m)^>?\s*Início da mensagem reencaminhada\s?:"),
    # Apple Mail (pt-br)
    re.compile(r"(?m)^>?\s*Início da mensagem encaminhada\s?:"),
    # Apple Mail (ro)
    re.compile(r"(?m)^>?\s*Începe mesajul redirecționat\s?:"),
    # Apple Mail (ro)
    re.compile(r"(?m)^>?\s*Начало переадресованного сообщения\s?:"),
    # Apple Mail (sk)
    re.compile(r"(?m)^>?\s*Začiatok preposlanej správy\s?:"),
    # Apple Mail (sv),
    re.compile(r"(?m)^>?\s*Vidarebefordrat mejl\s?:"),
    # Apple Mail (tr)
    re.compile(r"(?m)^>?\s*İleti başlangıcı\s?:"),
    # Apple Mail (uk)
    re.compile(r"(?m)^>?\s*Початок листа, що пересилається\s?:"),
    # Gmail (all locales), Missive (en), HubSpot (en)
    re.compile(r"(?m)^\s*-{8,10}\s*Forwarded message\s*-{8,10}\s*"),
    # Outlook Live / 365 (all locales)
    re.compile(r"(?m)^\s*_{32}\s*$"),
    # Outlook 2019 (cz)
    re.compile(r"(?m)^\s?Dne\s?.+\,\s?.+\s*[\[|<].+[\]|>]\s?napsal\(a\)\s?:"),
    # Outlook 2019 (da)
    re.compile(r"(?m)^\s?D.\s?.+\s?skrev\s?\".+\"\s*[\[|<].+[\]|>]\s?:"),
    # Outlook 2019 (de)
    re.compile(r"(?m)^\s?Am\s?.+\s?schrieb\s?\".+\"\s*[\[|<].+[\]|>]\s?:"),
    # Outlook 2019 (en)
    re.compile(r"(?m)^\s?On\s?.+\,\s?\".+\"\s*[\[|<].+[\]|>]\s?wrote\s?:"),
    # Outlook 2019 (es)
    re.compile(r"(?m)^\s?El\s?.+\,\s?\".+\"\s*[\[|<].+[\]|>]\s?escribió\s?:"),
    # Outlook 2019 (fr)
    re.compile(r"(?m)^\s?Le\s?.+\,\s?«.+»\s*[\[|<].+[\]|>]\s?a écrit\s?:"),
    # Outlook 2019 (fi)
    re.compile(r"(?m)^\s?.+\s*[\[|<].+[\]|>]\s?kirjoitti\s?.+\s?:"),
    # Outlook 2019 (hu)
    re.compile(r"(?m)^\s?.+\s?időpontban\s?.+\s*[\[|<|(].+[\]|>|)]\s?ezt írta\s?:"),
    # Outlook 2019 (it)
    re.compile(r"(?m)^\s?Il giorno\s?.+\s?\".+\"\s*[\[|<].+[\]|>]\s?ha scritto\s?:"),
    # Outlook 2019 (nl)
    re.compile(r"(?m)^\s?Op\s?.+\s?heeft\s?.+\s*[\[|<].+[\]|>]\s?geschreven\s?:"),
    # Outlook 2019 (no)
    re.compile(r"(?m)^\s?.+\s*[\[|<].+[\]|>]\s?skrev følgende den\s?.+\s?:"),
    # Outlook 2019 (pl)
    re.compile(r"(?m)^\s?Dnia\s?.+\s?„.+”\s*[\[|<].+[\]|>]\s?napisał\s?:"),
    # Outlook 2019 (pt)
    re.compile(r"(?m)^\s?Em\s?.+\,\s?\".+\"\s*[\[|<].+[\]|>]\s?escreveu\s?:"),
    # Outlook 2019 (ru)
    re.compile(r"(?m)^\s?.+\s?пользователь\s?\".+\"\s*[\[|<].+[\]|>]\s?написал\s?:"),
    # Outlook 2019 (sk)
    re.compile(r"(?m)^\s?.+\s?používateľ\s?.+\s*\([\[|<].+[\]|>]\)\s?napísal\s?:"),
    # Outlook 2019 (sv)
    re.compile(r"(?m)^\s?Den\s?.+\s?skrev\s?\".+\"\s*[\[|<].+[\]|>]\s?följande\s?:"),
    # Outlook 2019 (tr)
    re.compile(r"(?m)^\s?\".+\"\s*[\[|<].+[\]|>]\,\s?.+\s?tarihinde şunu yazdı\s?:"),
    # Yahoo Mail (cs), Thunderbird (cs)
    re.compile(r"(?m)^\s*-{5,8} Přeposlaná zpráva -{5,8}\s*"),
    # Yahoo Mail (da), Thunderbird (da)
    re.compile(r"(?m)^\s*-{5,8} Videresendt meddelelse -{5,8}\s*"),
    # Yahoo Mail (de), Thunderbird (de), HubSpot (de)
    re.compile(r"(?m)^\s*-{5,10} Weitergeleitete Nachricht -{5,10}\s*"),
    # Yahoo Mail (en), Thunderbird (en)
    re.compile(r"(?m)^\s*-{5,8} Forwarded Message -{5,8}\s*"),
    # Yahoo Mail (es), Thunderbird (es), HubSpot (es)
    re.compile(r"(?m)^\s*-{5,10} Mensaje reenviado -{5,10}\s*"),
    # Yahoo Mail (fi), HubSpot (fi)
    re.compile(r"(?m)^\s*-{5,10} Edelleenlähetetty viesti -{5,10}\s*"),
    # Yahoo Mail (fr)
    re.compile(r"(?m)^\s*-{5} Message transmis -{5}\s*"),
    # Yahoo Mail (hu), Thunderbird (hu)
    re.compile(r"(?m)^\s*-{5,8} Továbbított üzenet -{5,8}\s*"),
    # Yahoo Mail (it), HubSpot (it)
    re.compile(r"(?m)^\s*-{5,10} Messaggio inoltrato -{5,10}\s*"),
    # Yahoo Mail (nl), Thunderbird (nl), HubSpot (nl)
    re.compile(r"(?m)^\s*-{5,10} Doorgestuurd bericht -{5,10}\s*"),
    # Yahoo Mail (no), Thunderbird (no)
    re.compile(r"(?m)^\s*-{5,8} Videresendt melding -{5,8}\s*"),
    # Yahoo Mail (pl)
    re.compile(r"(?m)^\s*-{5} Przekazana wiadomość -{5}\s*"),
    # Yahoo Mail (pt), Thunderbird (pt)
    re.compile(r"(?m)^\s*-{5,8} Mensagem reencaminhada -{5,8}\s*"),
    # Yahoo Mail (pt-br), Thunderbird (pt-br), HubSpot (pt-br)
    re.compile(r"(?m)^\s*-{5,10} Mensagem encaminhada -{5,10}\s*"),
    # Yahoo Mail (ro)
    re.compile(r"(?m)^\s*-{5,8} Mesaj redirecționat -{5,8}\s*"),
    # Yahoo Mail (ru)
    re.compile(r"(?m)^\s*-{5} Пересылаемое сообщение -{5}\s*"),
    # Yahoo Mail (sk)
    re.compile(r"(?m)^\s*-{5} Preposlaná správa -{5}\s*"),
    # Yahoo Mail (sv), Thunderbird (sv), HubSpot (sv)
    re.compile(r"(?m)^\s*-{5,10} Vidarebefordrat meddelande -{5,10}\s*"),
    # Yahoo Mail (tr)
    re.compile(r"(?m)^\s*-{5} İletilmiş Mesaj -{5}\s*"),
    # Yahoo Mail (uk)
    re.compile(r"(?m)^\s*-{5} Перенаправлене повідомлення -{5}\s*"),
    # Thunderbird (fi)
    re.compile(r"(?m)^\s*-{8} Välitetty viesti \/ Fwd.Msg -{8}\s*"),
    # Thunderbird (fr), HubSpot (fr)
    re.compile(r"(?m)^\s*-{8,10} Message transféré -{8,10}\s*"),
    # Thunderbird (hr)
    re.compile(r"(?m)^\s*-{8} Proslijeđena poruka -{8}\s*"),
    # Thunderbird (it)
    re.compile(r"(?m)^\s*-{8} Messaggio Inoltrato -{8}\s*"),
    # Thunderbird (pl)
    re.compile(r"(?m)^\s*-{3} Treść przekazanej wiadomości -{3}\s*"),
    # Thunderbird (ru)
    re.compile(r"(?m)^\s*-{8} Перенаправленное сообщение -{8}\s*"),
    # Thunderbird (sk)
    re.compile(r"(?m)^\s*-{8} Preposlaná správa --- Forwarded Message -{8}\s*"),
    # Thunderbird (tr)
    re.compile(r"(?m)^\s*-{8} İletilen İleti -{8}\s*"),
    # Thunderbird (uk)
    re.compile(r"(?m)^\s*-{8} Переслане повідомлення -{8}\s*"),
    # HubSpot (ja)
    re.compile(r"(?m)^\s*-{9,10} メッセージを転送 -{9,10}\s*"),
    # HubSpot (pl)
    re.compile(r"(?m)^\s*-{9,10} Wiadomość przesłana dalej -{9,10}\s*"),
    # IONOS by 1 & 1 (en)
    re.compile(r"(?m)^>?\s*-{10} Original Message -{10}\s*"),
]

SEPARATOR_WITH_INFORMATION = [
    # Outlook 2019 (cz)
    re.compile(r"(?m)^\s?Dne\s?(?P<date>.+)\,\s?(?P<from_name>.+)\s*[\[|<](?P<from_address>.+)[\]|>]\s?napsal\(a\)\s?:"),
    # Outlook 2019 (da)
    re.compile(r"(?m)^\s?D.\s?(?P<date>.+)\s?skrev\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?:"),
    # Outlook 2019 (de)
    re.compile(r"(?m)^\s?Am\s?(?P<date>.+)\s?schrieb\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?:"),
    # Outlook 2019 (en)
    re.compile(r"(?m)^\s?On\s?(?P<date>.+)\,\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?wrote\s?:"),
    # Outlook 2019 (es)
    re.compile(r"(?m)^\s?El\s?(?P<date>.+)\,\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?escribió\s?:"),
    # Outlook 2019 (fr)
    re.compile(r"(?m)^\s?Le\s?(?P<date>.+)\,\s?«(?P<from_name>.+)»\s*[\[|<](?P<from_address>.+)[\]|>]\s?a écrit\s?:"),
    # Outlook 2019 (fi)
    re.compile(r"(?m)^\s?(?P<from_name>.+)\s*[\[|<](?P<from_address>.+)[\]|>]\s?kirjoitti\s?(?P<date>.+)\s?:"),
    # Outlook 2019 (hu)
    re.compile(r"(?m)^\s?(?P<date>.+)\s?időpontban\s?(?P<from_name>.+)\s*[\[|<|(](?P<from_address>.+)[\]|>|)]\s?ezt írta\s?:"),
    # Outlook 2019 (it)
    re.compile(r"(?m)^\s?Il giorno\s?(?P<date>.+)\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?ha scritto\s?:"),
    # Outlook 2019 (nl)
    re.compile(r"(?m)^\s?Op\s?(?P<date>.+)\s?heeft\s?(?P<from_name>.+)\s*[\[|<](?P<from_address>.+)[\]|>]\s?geschreven\s?:"),
    # Outlook 2019 (no)
    re.compile(r"(?m)^\s?(?P<from_name>.+)\s*[\[|<](?P<from_address>.+)[\]|>]\s?skrev følgende den\s?(?P<date>.+)\s?:"),
    # Outlook 2019 (pl)
    re.compile(r"(?m)^\s?Dnia\s?(?P<date>.+)\s?„(?P<from_name>.+)”\s*[\[|<](?P<from_address>.+)[\]|>]\s?napisał\s?:"),
    # Outlook 2019 (pt)
    re.compile(r"(?m)^\s?Em\s?(?P<date>.+)\,\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?escreveu\s?:"),
    # Outlook 2019 (ru)
    re.compile(r"(?m)^\s?(?P<date>.+)\s?пользователь\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?написал\s?:"),
    # Outlook 2019 (sk)
    re.compile(r"(?m)^\s?(?P<date>.+)\s?používateľ\s?(?P<from_name>.+)\s*\([\[|<](?P<from_address>.+)[\]|>]\)\s?napísal\s?:"),
    # Outlook 2019 (sv)
    re.compile(r"(?m)^\s?Den\s?(?P<date>.+)\s?skrev\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\s?följande\s?:"),
    # Outlook 2019 (tr)
    re.compile(r"(?m)^\s?\"(?P<from_name>.+)\"\s*[\[|<](?P<from_address>.+)[\]|>]\,\s?(?P<date>.+)\s?tarihinde şunu yazdı\s?:"),
]

ORIGINAL_SUBJECT = [
    # Apple Mail (en), Gmail (all locales), Outlook Live / 365 (all locales), New Outlook 2019 (en), Thunderbird (da, en), Missive (en), HubSpot (en)
    re.compile(r"(?im)^\*?Subject\s?:\*?(.+)"),
    # Apple Mail (cs), New Outlook 2019 (cs), Thunderbird (cs)
    re.compile(r"(?im)^Předmět\s?:(.+)"),
    # Apple Mail (da, no), New Outlook 2019 (da), Thunderbird (no)
    re.compile(r"(?im)^Emne\s?:(.+)"),
    # Apple Mail (de), New Outlook 2019 (de), Thunderbird (de), HubSpot (de)
    re.compile(r"(?im)^Betreff\s?:(.+)"),
    # Apple Mail (es), New Outlook 2019 (es), Thunderbird (es), HubSpot (es)
    re.compile(r"(?im)^Asunto\s?:(.+)"),
    # Apple Mail (fi), New Outlook 2019 (fi), Thunderbird (fi), HubSpot (fi)
    re.compile(r"(?im)^Aihe\s?:(.+)"),
    # Apple Mail (fr), New Outlook 2019 (fr), HubSpot (fr)
    re.compile(r"(?im)^Objet\s?:(.+)"),
    # Apple Mail (hr, sk), New Outlook 2019 (sk), Thunderbird (sk)
    re.compile(r"(?im)^Predmet\s?:(.+)"),
    # Apple Mail (hu), New Outlook 2019 (hu), Thunderbird (hu)
    re.compile(r"(?im)^Tárgy\s?:(.+)"),
    # Apple Mail (it), New Outlook 2019 (it), Thunderbird (it), HubSpot (it)
    re.compile(r"(?im)^Oggetto\s?:(.+)"),
    # Apple Mail (nl), New Outlook 2019 (nl), Thunderbird (nl), HubSpot (nl)
    re.compile(r"(?im)^Onderwerp\s?:(.+)"),
    # Apple Mail (pl), New Outlook 2019 (pl), Thunderbird (pl), HubSpot (pl)
    re.compile(r"(?im)^Temat\s?:(.+)"),
    # Apple Mail (pt, pt-br), New Outlook 2019 (pt, pt-br), Thunderbird (pt, pt-br), HubSpot (pt-br)
    re.compile(r"(?im)^Assunto\s?:(.+)"),
    # Apple Mail (ro), Thunderbird (ro)
    re.compile(r"(?im)^Subiectul\s?:(.+)"),
    # Apple Mail (ru, uk), New Outlook 2019 (ru), Thunderbird (ru, uk)
    re.compile(r"(?im)^Тема\s?:(.+)"),
    # Apple Mail (sv), New Outlook 2019 (sv), Thunderbird (sv), HubSpot (sv)
    re.compile(r"(?im)^Ämne\s?:(.+)"),
    # Apple Mail (tr), Thunderbird (tr)
    re.compile(r"(?im)^Konu\s?:(.+)"),
    # Thunderbird (fr)
    re.compile(r"(?im)^Sujet\s?:(.+)"),
    # Thunderbird (hr)
    re.compile(r"(?im)^Naslov\s?:(.+)"),
    # HubSpot (ja)
    re.compile(r"(?im)^件名：(.+)"),
]

ORIGINAL_SUBJECT_LAX = [
    # Yahoo Mail (en)
    re.compile(r"(?i)Subject\s?:(.+)"),
    # Yahoo Mail (da, no)
    re.compile(r"(?i)Emne\s?:(.+)"),
    # Yahoo Mail (cs)
    re.compile(r"(?i)Předmět\s?:(.+)"),
    # Yahoo Mail (de)
    re.compile(r"(?i)Betreff\s?:(.+)"),
    # Yahoo Mail (es)
    re.compile(r"(?i)Asunto\s?:(.+)"),
    # Yahoo Mail (fi)
    re.compile(r"(?i)Aihe\s?:(.+)"),
    # Yahoo Mail (fr)
    re.compile(r"(?i)Objet\s?:(.+)"),
    # Yahoo Mail (hu)
    re.compile(r"(?i)Tárgy\s?:(.+)"),
    # Yahoo Mail (it)
    re.compile(r"(?i)Oggetto\s?:(.+)"),
    # Yahoo Mail (nl)
    re.compile(r"(?i)Onderwerp\s?:(.+)"),
    # Yahoo Mail (pt, pt-br)
    re.compile(r"(?i)Assunto\s?:?(.+)"),
    # Yahoo Mail (pl)
    re.compile(r"(?i)Temat\s?:(.+)"),
    # Yahoo Mail (ro)
    re.compile(r"(?i)Subiect\s?:(.+)"),
    # Yahoo Mail (ru, uk)
    re.compile(r"(?i)Тема\s?:(.+)"),
    # Yahoo Mail (sk)
    re.compile(r"(?i)Predmet\s?:(.+)"),
    # Yahoo Mail (sv)
    re.compile(r"(?i)Ämne\s?:(.+)"),
    # Yahoo Mail (tr)
    re.compile(r"(?i)Konu\s?:(.+)"),
]

ORIGINAL_FROM = [
    # Apple Mail (en), Outlook Live / 365 (all locales), New Outlook 2019 (en), Thunderbird (da, en), Missive (en), HubSpot (en)
    re.compile(r"(?m)^(\*?\s*From\s?:\*?(.+))$"),
    # Apple Mail (cs, pl, sk), Gmail (cs, pl, sk), New Outlook 2019 (cs, pl, sk), Thunderbird (cs, sk), HubSpot (pl)
    re.compile(r"(?m)^(\s*Od\s?:(.+))$"),
    # Apple Mail (da, no), Gmail (da, no), New Outlook 2019 (da), Thunderbird (no)
    re.compile(r"(?m)^(\s*Fra\s?:(.+))$"),
    # Apple Mail (de), Gmail (de), New Outlook 2019 (de), Thunderbird (de), HubSpot (de)
    re.compile(r"(?m)^(\s*Von\s?:(.+))$"),
    # Apple Mail (es, fr, pt, pt-br), Gmail (es, fr, pt, pt-br), New Outlook 2019 (es, fr, pt, pt-br), Thunderbird (fr, pt, pt-br), HubSpot (es, fr, pt-br)
    re.compile(r"(?m)^(\s*De\s?:(.+))$"),
    # Apple Mail (fi), Gmail (fi), New Outlook 2019 (fi), Thunderbird (fi), HubSpot (fi)
    re.compile(r"(?m)^(\s*Lähettäjä\s?:(.+))$"),
    # Apple Mail (hr), Gmail (hr), Thunderbird (hr)
    re.compile(r"(?m)^(\s*Šalje\s?:(.+))$"),
    # Apple Mail (hu), Gmail (hu), New Outlook 2019 (fr), Thunderbird (hu)
    re.compile(r"(?m)^(\s*Feladó\s?:(.+))$"),
    # Apple Mail (it), Gmail (it), New Outlook 2019 (it), HubSpot (it)
    re.compile(r"(?m)^(\s*Da\s?:(.+))$"),
    # Apple Mail (nl), Gmail (nl), New Outlook 2019 (nl), Thunderbird (nl), HubSpot (nl)
    re.compile(r"(?m)^(\s*Van\s?:(.+))$"),
    # Apple Mail (ro)
    re.compile(r"(?m)^(\s*Expeditorul\s?:(.+))$"),
    # Apple Mail (ru)
    re.compile(r"(?m)^(\s*Отправитель\s?:(.+))$"),
    # Apple Mail (sv), Gmail (sv), New Outlook 2019 (sv), Thunderbird (sv), HubSpot (sv)
    re.compile(r"(?m)^(\s*Från\s?:(.+))$"),
    # Apple Mail (tr), Thunderbird (tr)
    re.compile(r"(?m)^(\s*Kimden\s?:(.+))$"),
    # Apple Mail (uk)
    re.compile(r"(?m)^(\s*Від кого\s`?:(.+))$"),
    # Gmail (et)
    re.compile(r"(?m)^(\s*Saatja\s?:(.+))$"),
    # Gmail (ro)
    re.compile(r"(?m)^(\s*De la\s`?:(.+))$"),
    # Gmail (tr)
    re.compile(r"(?m)^(\s*Gönderen\s?:(.+))$"),
    # Gmail (ru), New Outlook 2019 (ru), Thunderbird (ru)
    re.compile(r"(?m)^(\s*От\s?:(.+))$"),
    # Gmail (uk), Thunderbird (uk)
    re.compile(r"(?m)^(\s*Від\s?:(.+))$"),
    # Thunderbird (it)
    re.compile(r"(?m)^(\s*Mittente\s?:(.+))$"),
    # Thunderbird (pl)
    re.compile(r"(?m)^(\s*Nadawca\s?:(.+))$"),
    # Thunderbird (ro)
    re.compile(r"(?m)^(\s*de la\s`?:(.+))$"),
    # HubSpot (ja)
    re.compile(r"(?m)^(\s*送信元：(.+))$"),
]

ORIGINAL_FROM_LAX = [
    # Yahoo Mail (en)
    re.compile(r"(\s*From\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (cs, pl, sk)
    re.compile(r"(\s*Od\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (da, no)
    re.compile(r"(\s*Fra\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (de)
    re.compile(r"(\s*Von\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (es, fr, pt, pt-br)
    re.compile(r"(\s*De\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (fi)
    re.compile(r"(\s*Lähettäjä\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (hu)
    re.compile(r"(\s*Feladó\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (it)
    re.compile(r"(\s*Da\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (nl)
    re.compile(r"(\s*Van\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (ro)
    re.compile(r"(\s*De la\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (ru)
    re.compile(r"(\s*От\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (sv)
    re.compile(r"(\s*Från\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (tr)
    re.compile(r"(\s*Kimden\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
    # Yahoo Mail (uk)
    re.compile(r"(\s*Від\s?:(.+?)\s?\n?\s*[\[|<](.+?)[\]|>])"),
]

ORIGINAL_TO = [
    # Apple Mail (en), Gmail (all locales), Outlook Live / 365 (all locales), Thunderbird (da, en), Missive (en), HubSpot (en)
    re.compile(r"(?m)^\*?\s*To\s?:\*?(.+)$"),
    # Apple Mail (cs), New Outlook 2019 (cs, sk), Thunderbird (cs)
    re.compile(r"(?m)^\s*Komu\s?:(.+)$"),
    # Apple Mail (da, no), New Outlook 2019 (da), Thunderbird (no)
    re.compile(r"(?m)^\s*Til\s?:(.+)$"),
    # Apple Mail (de), New Outlook 2019 (de), Thunderbird (de), HubSpot (de)
    re.compile(r"(?m)^\s*An\s?:(.+)$"),
    # Apple Mail (es, pt, pt-br), New Outlook 2019 (es, pt, pt-br), Thunderbird (es, pt, pt-br), HubSpot (pt-br)
    re.compile(r"(?m)^\s*Para\s?:(.+)$"),
    # Apple Mail (fi), New Outlook 2019 (fi), Thunderbird (fi), HubSpot (fi)
    re.compile(r"(?m)^\s*Vastaanottaja\s?:(.+)$"),
    # Apple Mail (fr), New Outlook 2019 (fr), HubSpot (fr)
    re.compile(r"(?m)^\s*À\s?:(.+)$"),
    # Apple Mail (hr), Thunderbird (hr)
    re.compile(r"(?m)^\s*Prima\s?:(.+)$"),
    # Apple Mail (hu), New Outlook 2019 (hu), Thunderbird (hu)
    re.compile(r"(?m)^\s*Címzett\s?:(.+)$"),
    # Apple Mail (it), New Outlook 2019 (it), Thunderbird (it), HubSpot (es, it)
    re.compile(r"(?m)^\s*A\s?:(.+)$"),
    # Apple Mail (nl), New Outlook 2019 (nl), Thunderbird (nl), HubSpot (nl)
    re.compile(r"(?m)^\s*Aan\s?:(.+)$"),
    # Apple Mail (pl), New Outlook 2019 (pl), HubSpot (pl)
    re.compile(r"(?m)^\s*Do\s?:(.+)$"),
    # Apple Mail (ro)
    re.compile(r"(?m)^\s*Destinatarul\s?:(.+)$"),
    # Apple Mail (ru, uk), New Outlook 2019 (ru), Thunderbird (ru, uk)
    re.compile(r"(?m)^\s*Кому\s?:(.+)$"),
    # Apple Mail (sk), Thunderbird (sk)
    re.compile(r"(?m)^\s*Pre\s?:(.+)$"),
    # Apple Mail (sv), New Outlook 2019 (sv), Thunderbird (sv)
    re.compile(r"(?m)^\s*Till\s?:(.+)$"),
    # Apple Mail (tr), Thunderbird (tr)
    re.compile(r"(?m)^\s*Kime\s?:(.+)$"),
    # Thunderbird (fr)
    re.compile(r"(?m)^\s*Pour\s?:(.+)$"),
    # Thunderbird (pl)
    re.compile(r"(?m)^\s*Adresat\s?:(.+)$"),
    # HubSpot (ja)
    re.compile(r"(?m)^\s*送信先：(.+)$"),
]

ORIGINAL_TO_LAX = [
    # Yahook Mail (en)
    re.compile(r"(?m)\s*To\s?:(.+)$"),
    # Yahook Mail (cs, sk)
    re.compile(r"(?m)\s*Komu\s?:(.+)$"),
    # Yahook Mail (da, no, sv)
    re.compile(r"(?m)\s*Til\s?:(.+)$"),
    # Yahook Mail (de)
    re.compile(r"(?m)\s*An\s?:(.+)$"),
    # Yahook Mail (es, pt, pt-br)
    re.compile(r"(?m)\s*Para\s?:(.+)$"),
    # Yahook Mail (fi)
    re.compile(r"(?m)\s*Vastaanottaja\s?:(.+)$"),
    # Yahook Mail (fr)
    re.compile(r"(?m)\s*À\s?:(.+)$"),
    # Yahook Mail (hu)
    re.compile(r"(?m)\s*Címzett\s?:(.+)$"),
    # Yahook Mail (it)
    re.compile(r"(?m)\s*A\s?:(.+)$"),
    # Yahook Mail (nl)
    re.compile(r"(?m)\s*Aan\s?:(.+)$"),
    # Yahook Mail (pl)
    re.compile(r"(?m)\s*Do\s?:(.+)$"),
    # Yahook Mail (ro), Thunderbird (ro)
    re.compile(r"(?m)\s*Către\s?:(.+)$"),
    # Yahook Mail (ru, uk)
    re.compile(r"(?m)\s*Кому\s?:(.+)$"),
    # Yahook Mail (sv)
    re.compile(r"(?m)\s*Till\s?:(.+)$"),
    # Yahook Mail (tr)
    re.compile(r"(?m)\s*Kime\s?:(.+)$"),
]

ORIGINAL_REPLY_TO = [
    # Apple Mail (en)
    re.compile(r"(?m)^\s*Reply-To\s?:(.+)$"),
    # Apple Mail (hr)
    re.compile(r"(?m)^\s*Odgovori na\s?:(.+)$"),
    # Apple Mail (cs)
    re.compile(r"(?m)^\s*Odpověď na\s?:(.+)$"),
    # Apple Mail (da)
    re.compile(r"(?m)^\s*Svar til\s?:(.+)$"),
    # Apple Mail (nl)
    re.compile(r"(?m)^\s*Antwoord aan\s?:(.+)$"),
    # Apple Mail (fi)
    re.compile(r"(?m)^\s*Vastaus\s?:(.+)$"),
    # Apple Mail (fr)
    re.compile(r"(?m)^\s*Répondre à\s?:(.+)$"),
    # Apple Mail (de)
    re.compile(r"(?m)^\s*Antwort an\s?:(.+)$"),
    # Apple Mail (hu)
    re.compile(r"(?m)^\s*Válaszcím\s?:(.+)$"),
    # Apple Mail (it)
    re.compile(r"(?m)^\s*Rispondi a\s?:(.+)$"),
    # Apple Mail (no)
    re.compile(r"(?m)^\s*Svar til\s?:(.+)$"),
    # Apple Mail (pl)
    re.compile(r"(?m)^\s*Odpowiedź-do\s?:(.+)$"),
    # Apple Mail (pt)
    re.compile(r"(?m)^\s*Responder A\s?:(.+)$"),
    # Apple Mail (pt-br, es)
    re.compile(r"(?m)^\s*Responder a\s?:(.+)$"),
    # Apple Mail (ro)
    re.compile(r"(?m)^\s*Răspuns către\s?:(.+)$"),
    # Apple Mail (ru)
    re.compile(r"(?m)^\s*Ответ-Кому\s?:(.+)$"),
    # Apple Mail (sk)
    re.compile(r"(?m)^\s*Odpovedať-Pre\s?:(.+)$"),
    # Apple Mail (sv)
    re.compile(r"(?m)^\s*Svara till\s?:(.+)$"),
    # Apple Mail (tr)
    re.compile(r"(?m)^\s*Yanıt Adresi\s?:(.+)$"),
    # Apple Mail (uk)
    re.compile(r"(?m)^\s*Кому відповісти\s?:(.+)$"),
]

ORIGINAL_CC = [
    # Apple Mail (en, da, es, fr, hr, it, pt, pt-br, ro, sk), Gmail (all locales), Outlook Live / 365 (all locales),
    # New Outlook 2019 (da, de, en, fr, it, pt-br), Missive (en), HubSpot (de, en, es, it, nl, pt-br)
    re.compile(r"(?m)^\*?\s*Cc\s?:\*?(.+)$"),
    # New Outlook 2019 (es, nl, pt), Thunderbird (da, en, es, fi, hr, hu, it, nl, no, pt, pt-br, ro, tr, uk)
    re.compile(r"(?m)^\s*CC\s?:(.+)$"),
    # Apple Mail (cs, de, nl), New Outlook 2019 (cs), Thunderbird (cs)
    re.compile(r"(?m)^\s*Kopie\s?:(.+)$"),
    # Apple Mail (fi), New Outlook 2019 (fi), HubSpot (fi)
    re.compile(r"(?m)^\s*Kopio\s?:(.+)$"),
    # Apple Mail (hu)
    re.compile(r"(?m)^\s*Másolat\s?:(.+)$"),
    # Apple Mail (no)
    re.compile(r"(?m)^\s*Kopi\s?:(.+)$"),
    # Apple Mail (pl)
    re.compile(r"(?m)^\s*Dw\s?:(.+)$"),
    # Apple Mail (ru), New Outlook 2019 (ru), Thunderbird (ru)
    re.compile(r"(?m)^\s*Копия\s?:(.+)$"),
    # Apple Mail (sv), New Outlook 2019 (sv), Thunderbird (pl, sv), HubSpot (sv)
    re.compile(r"(?m)^\s*Kopia\s?:(.+)$"),
    # Apple Mail (tr)
    re.compile(r"(?m)^\s*Bilgi\s?:(.+)$"),
    # Apple Mail (uk),
    re.compile(r"(?m)^\s*Копія\s?:(.+)$"),
    # New Outlook 2019 (hu)
    re.compile(r"(?m)^\s*Másolatot kap\s?:(.+)$"),
    # New Outlook 2019 (sk), Thunderbird (sk)
    re.compile(r"(?m)^\s*Kópia\s?:(.+)$"),
    # New Outlook 2019 (pl), HubSpot (pl)
    re.compile(r"(?m)^\s*DW\s?:(.+)$"),
    # Thunderbird (de)
    re.compile(r"(?m)^\s*Kopie \(CC\)\s?:(.+)$"),
    # Thunderbird (fr)
    re.compile(r"(?m)^\s*Copie à\s?:(.+)$"),
    # HubSpot (ja)
    re.compile(r"(?m)^\s*CC：(.+)$"),
]

ORIGINAL_CC_LAX = [
    # Yahoo Mail (da, en, it, nl, pt, pt-br, ro, tr)
    re.compile(r"(?m)\s*Cc\s?:(.+)$"),
    # Yahoo Mail (de, es)
    re.compile(r"(?m)\s*CC\s?:(.+)$"),
    # Yahoo Mail (cs)
    re.compile(r"(?m)\s*Kopie\s?:(.+)$"),
    # Yahoo Mail (fi)
    re.compile(r"(?m)\s*Kopio\s?:(.+)$"),
    # Yahoo Mail (hu)
    re.compile(r"(?m)\s*Másolat\s?:(.+)$"),
    # Yahoo Mail (no)
    re.compile(r"(?m)\s*Kopi\s?:(.+)$"),
    # Yahoo Mail (pl)
    re.compile(r"(?m)\s*Dw\s?(.+)$"),
    # Yahoo Mail (ru)
    re.compile(r"(?m)\s*Копия\s?:(.+)$"),
    # Yahoo Mail (sk)
    re.compile(r"(?m)\s*Kópia\s?:(.+)$"),
    # Yahoo Mail (sv)
    re.compile(r"(?m)\s*Kopia\s?:(.+)$"),
    # Yahoo Mail (uk)
    re.compile(r"(?m)\s*Копія\s?:(.+)$"),
]

ORIGINAL_DATE = [
    # Apple Mail (en, fr), Gmail (all locales), New Outlook 2019 (en, fr), Thunderbird (da, en, fr), Missive (en), HubSpot (en, fr)
    re.compile(r"(?m)^\s*Date\s?:(.+)$"),
    # Apple Mail (cs, de, hr, nl, sv), New Outlook 2019 (cs, de, nl, sv), Thunderbird (cs, de, hr, nl, sv), HubSpot (de, nl, sv)
    re.compile(r"(?m)^\s*Datum\s?:(.+)$"),
    # Apple Mail (da, no), New Outlook 2019 (da), Thunderbird (no)
    re.compile(r"(?m)^\s*Dato\s?:(.+)$"),
    # New Outlook 2019 (fr)
    re.compile(r"(?m)^\s*Envoyé\s?:(.+)$"),
    # Apple Mail (es), New Outlook 2019 (es), Thunderbird (es), HubSpot (es)
    re.compile(r"(?m)^\s*Fecha\s?:(.+)$"),
    # Apple Mail (fi), New Outlook 2019 (fi), HubSpot (fi)
    re.compile(r"(?m)^\s*Päivämäärä\s?:(.+)$"),
    # Apple Mail (hu, sk), New Outlook 2019 (sk), Thunderbird (hu, sk)
    re.compile(r"(?m)^\s*Dátum\s?:(.+)$"),
    # Apple Mail (it, pl, pt, pt-br), New Outlook 2019 (it, pl, pt, pt-br), Thunderbird (it, pl, pt, pt-br), HubSpot (it, pl, pt-br)
    re.compile(r"(?m)^\s*Data\s?:(.+)$"),
    # Apple Mail (ro), Thunderbird (ro)
    re.compile(r"(?m)^\s*Dată\s?:(.+)$"),
    re.compile(r"(?m)^\s*Дата\s?:(.+)$"),
    # Apple Mail (ru, uk), New Outlook 2019 (ru), Thunderbird (ru, uk)
    re.compile(r"(?m)^\s*Tarih\s?:(.+)$"),  # Apple Mail (tr), Thunderbird (tr)
    # Outlook Live / 365 (all locales)
    re.compile(r"(?m)^\*?\s*Sent\s?:\*?(.+)$"),
    # Thunderbird (fi)
    re.compile(r"(?m)^\s*Päiväys\s?:(.+)$"),
    # HubSpot (ja)
    re.compile(r"(?m)^\s*日付：(.+)$"),
]

ORIGINAL_DATE_LAX = [
    # Yahoo Mail (cs)
    re.compile(r"(?m)\s*Datum\s?:(.+)$"),
    # Yahoo Mail (da, no)
    re.compile(r"(?m)\s*Sendt\s?:(.+)$"),
    # Yahoo Mail (de)
    re.compile(r"(?m)\s*Gesendet\s?:(.+)$"),
    # Yahoo Mail (en)
    re.compile(r"(?m)\s*Sent\s?:(.+)$"),
    # Yahoo Mail (es, pt, pt-br)
    re.compile(r"(?m)\s*Enviado\s?:(.+)$"),
    # Yahoo Mail (fr)
    re.compile(r"(?m)\s*Envoyé\s?:(.+)$"),
    # Yahoo Mail (fi)
    re.compile(r"(?m)\s*Lähetetty\s?:(.+)$"),
    # Yahoo Mail (hu)
    re.compile(r"(?m)\s*Elküldve\s?:(.+)$"),
    # Yahoo Mail (it)
    re.compile(r"(?m)\s*Inviato\s?:(.+)$"),
    # Yahoo Mail (it)
    re.compile(r"(?m)\s*Verzonden\s?:(.+)$"),
    # Yahoo Mail (pl)
    re.compile(r"(?m)\s*Wysłano\s?:(.+)$"),
    # Yahoo Mail (ro)
    re.compile(r"(?m)\s*Trimis\s?:(.+)$"),
    # Yahoo Mail (ru)
    re.compile(r"(?m)\s*Отправлено\s?:(.+)$"),
    # Yahoo Mail (sk)
    re.compile(r"(?m)\s*Odoslané\s?:(.+)$"),
    # Yahoo Mail (sv)
    re.compile(r"(?m)\s*Skickat\s?:(.+)$"),
    # Yahoo Mail (tr)
    re.compile(r"(?m)\s*Gönderilen\s?:(.+)$"),
    # Yahoo Mail (uk)
    re.compile(r"(?m)\s*Відправлено\s?:(.+)$"),
]

MAILBOX = [
    # "<walter.sheltan@acme.com<mailto:walter.sheltan@acme.com>>"
    re.compile(r"^\s?\n?\s*<.+?<mailto\:(.+?)>>"),
    # "Walter Sheltan <walter.sheltan@acme.com<mailto:walter.sheltan@acme.com>>"
    re.compile(r"^(.+?)\s?\n?\s*<.+?<mailto\:(.+?)>>"),
    # "Walter Sheltan <mailto:walter.sheltan@acme.com>" or "Walter Sheltan [mailto:walter.sheltan@acme.com]" or "walter.sheltan@acme.com <mailto:walter.sheltan@acme.com>"
    re.compile(r"^(.+?)\s?\n?\s*[\[|<]mailto\:(.+?)[\]|>]"),
    # "'Walter Sheltan' <walter.sheltan@acme.com>" or "'Walter Sheltan' [walter.sheltan@acme.com]" or "'walter.sheltan@acme.com' <walter.sheltan@acme.com>"
    re.compile(r"^\'(.+?)\'\s?\n?\s*[\[|<](.+?)[\]|>]"),
    # ""'Walter Sheltan'" <walter.sheltan@acme.com>" or ""'Walter Sheltan'" [walter.sheltan@acme.com]" or ""'walter.sheltan@acme.com'" <walter.sheltan@acme.com>"
    re.compile(r"^\"\'(.+?)\'\"\s?\n?\s*[\[|<](.+?)[\]|>]"),
    # ""Walter Sheltan" <walter.sheltan@acme.com>" or ""Walter Sheltan" [walter.sheltan@acme.com]" or ""walter.sheltan@acme.com" <walter.sheltan@acme.com>"
    re.compile(r"^\"(.+?)\"\s?\n?\s*[\[|<](.+?)[\]|>]"),
    # "Walter Sheltan <walter.sheltan@acme.com>" or "Walter Sheltan [walter.sheltan@acme.com]" or "walter.sheltan@acme.com <walter.sheltan@acme.com>"
    re.compile(r"^([^,;]+?)\s?\n?\s*[\[|<](.+?)[\]|>]"),
    # "<walter.sheltan@acme.com>"
    re.compile(r"^(.?)\s?\n?\s*[\[|<](.+?)[\]|>]"),
    # "walter.sheltan@acme.com"
    re.compile(r"^([^\s@]+@[^\s@]+\.[^\s@,]+)"),
    # "Walter, Sheltan <walter.sheltan@acme.com>" or "Walter, Sheltan [walter.sheltan@acme.com]"
    re.compile(r"^([^;].+?)\s?\n?\s*[\[|<](.+?)[\]|>]"),
]

MAILBOX_ADDRESS = [re.compile(r"^(([^\s@]+)@([^\s@]+)\.*([^\s@]+))$")]
