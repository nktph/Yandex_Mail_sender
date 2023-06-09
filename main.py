import asyncio
from email.mime.text import MIMEText
from aiosmtplib import SMTP


def split_list(lst, chunks=3):
    total_count = len(lst)
    chunk_size = -(-total_count // chunks)

    result = []
    for i in range(chunks):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size - 1
        part = lst[start_index:end_index + 1]
        result.append(part)
    return result


async def work(smtp_connection, username, recipients: list[str], percent: int, date: str, btn_link: str):

    header = f"Активируйте промокод на {percent}%"
    first_block = f"Промокод действует до {date}."
    second_block = "Предложение действует только при заказе онлайн."
    third_block = "Данная акция действует на всю продукцию в магазине."
    fourth_block = "К одному чеку можно применить неограниченное количество позиций."
    fifth_block = "Спасибо, что выбираете наш магазин."
    link_text = "Активировать промокод"
    html_content = f'''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <html lang="ru">
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <table border="0" cellpadding="0" cellspacing="0" style="margin:0; padding:0">
      <tr>
          <td class="m_2772788490390005054column m_2772788490390005054column-1" width="100%" style="font-weight:400;text-align:left;padding-bottom:25px;padding-left:40px;padding-right:40px;padding-top:30px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0">
              <table class="m_2772788490390005054text_block m_2772788490390005054block-1" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="word-break:break-word">
                  <tbody>
                  <tr>
                      <td class="m_2772788490390005054pad" style="padding-bottom:10px">
                          <div style="font-family:sans-serif">
                              <div style="font-size:14px;color:#1a202e;line-height:1.2;font-family:Arial,Helvetica Neue,Helvetica,sans-serif">
                                  <p style="margin:0;font-size:14px;text-align:center"><span style="font-size:28px;color:#1a202e">
                                      <strong>{header}</strong><br><br>
                                  </span>
                                  </p>
                              </div>
                          </div>
                      </td>
                  </tr>
                  </tbody>
              </table>
              <table class="m_2772788490390005054text_block m_2772788490390005054block-2" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="word-break:break-word">
                  <tbody>
                  <tr>
                      <td class="m_2772788490390005054pad">
                          <div style="font-family:sans-serif">
                              <div style="font-size:12px;text-align:left;color:#1a202e;line-height:1.5;font-family:Arial,Helvetica Neue,Helvetica,sans-serif">
                                  <p style="margin:0">
                                      <span style="font-size:24px">{first_block}<br>
                                                                    {second_block}<br>
                                                                    {third_block}<br>
                                                                    {fourth_block}<br>
                                                                    {fifth_block}
                                      </span>
                                  </p>
                                  <br><br>
                                  <p style="margin:0">
            <div style="width: 40%; margin-left: 30%;">
            <span style="font-size:24px">
                <a href="{btn_link}"
                       style="text-decoration:none;
                       display:block;
                       color:#ffffff;
                       background-color:#f75757;
                       border-radius:4px;width:95%;
                       border-top:0px solid transparent;
                       font-weight:400;
                       border-right:0px solid transparent;
                       border-bottom:0px solid transparent;
                       border-left:0px solid transparent;
                       padding-top:10px;
                       padding-bottom:10px;
                       font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;
                       font-size:18px;text-align:center;
                       word-break:keep-all" target="_blank">
                        <span style="padding-left:30%;
                        padding-right:30%;
                        font-size:18px;
                        display:inline-block;
                        letter-spacing:normal">
                            <span dir="ltr"
                                  style="word-break:keep-all;
                                  line-height:20px">
                                <strong>{link_text}</strong>
                            </span>
                        </span>
                    </a></span>
                              </div>
                                  </p>
                              </div>
                          </div>
                      </td>
                  </tr>
                  </tbody>
              </table>
          </td>
      </tr>
    </table>
    </body>
    </html>
    '''
    log = ""
    try:
        for recipient in recipients:
            message = MIMEText(html_content, 'html')
            message['Subject'] = f'Вам присвоен промокод на {percent}%'
            message['From'] = username
            message['To'] = recipient
            print(f"Отправляем {recipient}")
            try:
                async with asyncio.Lock():
                    await smtp_connection.send_message(message)
                print(f"Отправлено {recipient}")
                recipients.remove(recipient)
            except Exception as e:
                if '550' in str(e) or '501' in str(e):
                    print(e)
                    recipients.remove(recipient)
                    continue
                else:
                    raise e
    except Exception as e:
        log = f"В процессе отправки {recipient} возникла ошибка:\n{e}\nРассылка экстренно завершена."
        print(log)
        async with asyncio.Lock():
            with open("recipients.txt", 'w') as file:
                file.writelines(recipients)
        return log
    log = "Рассылка успешно завершена"
    print(log)
    return log


async def start(recipients: list[str], percent: int, date: str, btn_link: str):
    # Делим список получателей на 4 части
    list_chunks = split_list(recipients, chunks=4)

    with open("account.txt", 'r') as file:
        data = file.readline()
        username = data.split(':')[0].strip()
        password = data.split(':')[1].strip()

    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    async with SMTP(hostname=smtp_server, port=smtp_port, start_tls=True) as smtp_connection:
        # Авторизуемся в почтовом клиенте
        await smtp_connection.login(username, password)
        # Выделяем работягу на каждый кусок списка
        tasks = []
        for chunk in list_chunks:
            task = work(smtp_connection, username, chunk, percent, date, btn_link)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        await smtp_connection.quit()
    log = ""
    i = 0
    for result_log in results:
        i += 1
        log += f"{i}: {result_log}\n\n"
    return log
