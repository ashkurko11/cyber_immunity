import base64

VERIFIER_SEAL = 'verifier_seal' # строка-подпись, используется как простой маркер целостности и доверия

def check_payload_seal(payload): # функция убедиться, что данные не были изменены и были подписаны надёжным источником
    try:
        p = base64.b64decode(payload).decode()
        if p.endswith(VERIFIER_SEAL):
            print('[info] payload seal is valid')
            return True
    except Exception as e:
        print(f'[error] seal check error: {e}')
    return False


def check_operation(id, details):
    authorized = False
    print(f"[info] checking policies for event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")

    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']

    # Связь -> Брокер (начало запроса)
    if src == 'connection' and dst == 'broker' and operation == 'request_recipe':
        authorized = True

    # Брокер -> Хранилище рецептов 
    if src == 'broker' and dst == 'recipe_storage' and operation == 'get_recipe':
        authorized = True

    # Хранилище рецептов -> Брокер 
    if src == 'recipe_storage' and dst == 'broker' and operation == 'recipe_found':
        authorized = True

    # Брокер -> Система верификации рецептов 
    if src == 'broker' and dst == 'recipe_verifier' and operation == 'verify_recipe':
        authorized = True

    # Система верификации рецептов <-> Хранилище рецептов 
    if src == 'recipe_verifier' and dst == 'recipe_storage' and operation == 'get_recipe_data':
        authorized = True
    if src == 'recipe_storage' and dst == 'recipe_verifier' and operation == 'recipe_data':
        authorized = True

    # Система верификации -> Контроль конфигурации 
    if src == 'recipe_verifier' and dst == 'config_control' and operation == 'recipe_verified':
        authorized = True

    # Брокер -> Контроль конфигурации 
    if src == 'broker' and dst == 'config_control' and operation == 'control_request':
        authorized = True

    # Контроль конфигурации <-> Система управления роботом 
    if src == 'config_control' and dst == 'robot_control' and operation == 'apply_recipe':
        authorized = True
    if src == 'robot_control' and dst == 'config_control' and operation == 'report_state':
        authorized = True

    # Система управления роботом -> Брокер 
    if src == 'robot_control' and dst == 'broker' and operation == 'status_report':
        authorized = True

    #  Система управления роботом -> Система самодиагностики 
    if src == 'robot_control' and dst == 'self_diagnosis' and operation == 'request_diagnostics':
        authorized = True

    #  Система самодиагностики -> Брокер 
    if src == 'self_diagnosis' and dst == 'broker' and operation == 'diagnostic_result':
        authorized = True

    # Брокер -> Монитор безопасности 
    if src == 'broker' and dst == 'security_monitor' and operation == 'log_event':
        authorized = True

    #  Монитор безопасности -> Брокер 
    if src == 'security_monitor' and dst == 'broker' and operation == 'alert':
        authorized = True

    # Верифицированная передача рецепта в управление роботом 
    if src == 'broker' and dst == 'robot_control' and operation == 'apply_verified_recipe':
        if details.get('verified') and check_payload_seal(details.get('blob', '')):
            authorized = True

    # Робот-фармацевт -> Брокер
    if src == 'pharma_robot' and dst == 'broker' and operation == 'ready_product':
        authorized = True

    # Брокер -> Связь (выдача готового лекарства пользователю)
    if src == 'broker' and dst == 'connection' and operation == 'deliver_product':
        if details.get('verified') and check_payload_seal(details.get('product_blob', '')):
            authorized = True

    return authorized
