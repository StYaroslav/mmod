import numpy as np
import matplotlib.pyplot as plt
import colorama

from models.SimulationResults import SimulationResults
from models.TheoreticalResults import TheoreticalResults

MAX_TIME = 1000
CURRENT_TIME = 0


def generate_requests(lambda_value):
    requests = []
    time = 0
    while time < MAX_TIME:
        time += np.random.exponential(1 / lambda_value)
        requests.append(time)
    return requests


def get_next_item():
    global requests1, requests2, smo

    min_request1 = min(requests1)
    min_request2 = min(requests2)
    min_smo = None if len(smo) == 0 else min(smo)

    min_of_min = min([q for q in [min_request1, min_request2, min_smo] if q is not None])
    if min_of_min == min_request1:
        return 'request1', min_of_min
    if min_of_min == min_request2:
        return 'request2', min_of_min
    if min_of_min == min_smo:
        return 'smo', min_of_min


def get_theoretical_values(theoreticalResults):
    lambda_value = X1 + X2
    ro = lambda_value / mu

    p0 = 1 / (1 + ro / 1 + (ro ** 2) / 2)
    p1 = ro * p0
    p2 = (ro ** 2) * p0 / 2
    theoreticalResults.p = [p0, p1, p2]

    theoreticalResults.busy_channels = ro * (1 - p2)
    theoreticalResults.Q = 1 - p2
    theoreticalResults.A = lambda_value * (1 - p2)


def get_empirical_values(s1, s2, f1, f2, channels, simulationResult):
    simulationResult.empirical_p = [t / MAX_TIME for t in simulationResult.empirical_p]

    simulationResult.p_reject1 = f1 / (f1 + s1)
    simulationResult.p_reject2 = f2 / (f2 + s2)
    simulationResult.p_reject = (f1 + f2) / (f1 + f2 + s1 + s2)

    simulationResult.busy_channels = channels / MAX_TIME
    simulationResult.Q = 1 - simulationResult.p_reject
    simulationResult.A1 = s1 / MAX_TIME
    simulationResult.A2 = s2 / MAX_TIME


def show_plots(theoretical_p, empirical_p):
    s = [60 for _ in range(n + 1)]
    x = [i for i in range(n + 1)]
    plt.scatter(x, theoretical_p, s=s, c='red')
    plt.plot(x, theoretical_p, c='red')
    plt.scatter(x, empirical_p, s=s, c='blue')
    plt.plot(x, empirical_p, c='blue')
    plt.legend(['theoretical', 'empirical'])
    plt.show()


if __name__ == '__main__':
    n = 2
    X1 = 4
    X2 = 2
    mu = 5

    requests1 = generate_requests(X1)
    requests2 = generate_requests(X2)

    simulationResults = SimulationResults
    theoreticalResults = TheoreticalResults

    smo = []
    smo_type = []

    simulationResults.empirical_p = [0 for _ in range(n + 1)]
    channels = 0
    success1, success2, failure1, failure2 = 0, 0, 0, 0

    while CURRENT_TIME < MAX_TIME:
        event_name, time = get_next_item()

        channels += len(smo) * (time - CURRENT_TIME)
        simulationResults.empirical_p[len(smo)] += time - CURRENT_TIME

        if event_name == 'request2':
            requests2.remove(time)

            if len(smo) == n:   # Для заявки 2 не нашлось места
                failure2 += 1

            else:   # Если есть пустое место, добавляем заявку
                smo.append(time + np.random.exponential(1 / mu))
                smo_type.insert(len(smo) - 1, '2')

        if event_name == 'request1':
            requests1.remove(time)
            if len(smo) < n:    # Если есть пустое место, добавляем заявку
                smo.append(time + np.random.exponential(1 / mu))
                smo_type.insert(len(smo) - 1, '1')
            elif '2' in smo_type:   # В смо есть заявка второго типа
                index = smo_type.index('2')
                smo[index] = time + np.random.exponential(1 / mu)
                smo_type[index] = '1'

                failure2 += 1
            else:   # Нет места
                failure1 += 1

        if event_name == 'smo':     # Обработка заявки закончилась
            index = smo.index(time)

            if smo_type[index] == '1':
                success1 += 1
            else:
                success2 += 1

            del smo[index]
            del smo_type[index]

        CURRENT_TIME = time

    get_theoretical_values(theoreticalResults)
    get_empirical_values(success1, success2, failure1, failure2, channels, simulationResults)

    print(colorama.Fore.GREEN + 'Общие данные')
    print(colorama.Fore.RESET)
    print(f'Вероятность отказа для заявок первого типа: {simulationResults.p_reject1}')
    print(f'Вероятность отказа для заявок второго типа: {simulationResults.p_reject2}')
    print(f'Среднее число обслуженных заявок первого типа: {simulationResults.A1}')
    print(f'Среднее число обслуженных заявок второго типа: {simulationResults.A2}')
    print(f'Среднее число каналов, занятых обслуживанием заявок: {simulationResults.busy_channels}')

    print(colorama.Fore.GREEN + 'Сравнительная оценка')
    print(colorama.Fore.RESET)
    print(f'Относительная пропускная способность: теор: {theoreticalResults.Q}, эмпир: {simulationResults.Q}')
    print(f'Абсолютная пропускная способность: теор: {theoreticalResults.A}, эмпир: {simulationResults.A1 + simulationResults.A2}')
    print(f'Среднее число каналов, занятых обслуживанием заявок: теор: {theoreticalResults.busy_channels}, эмпир: {simulationResults.busy_channels}')
    print(f'{theoreticalResults.p} - теоретические финальные вероятности')
    print(f'{simulationResults.empirical_p} - эмпирические финальные вероятности')
    print(f'Вероятность отказа: теор: {theoreticalResults.p[-1]}, эмпир: {simulationResults.p_reject} или {simulationResults.empirical_p[-1]}')
    show_plots(theoreticalResults.p, simulationResults.empirical_p)
