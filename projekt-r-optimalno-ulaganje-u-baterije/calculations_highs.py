import pyomo.environ as pyo
from pyomo.environ import (
    ConcreteModel, Var, NonNegativeReals, RangeSet, Objective, Constraint,
    Param, Expression, SolverFactory, value
)


def gigaracun(values):
    """
    Pyomo, HiGHS
    """

    # Obrada ulaza: values
    D__tm = values[0]
    velicina_battery = values[1][0]
    VT = values[1][1]
    NT = values[1][2]
    C_p = values[1][3]
    # print(f"Uneseni parametri su: {values[1]}")

    months = 12
    T_hours = 24
    days_per_month = 30
    T_per_month = T_hours * days_per_month  # 720 = 30*24

    # mjesečna najveća potrošnja
    p_peak_vrijednosti = []
    for m in range(months):
        start = m * T_per_month
        end = start + T_per_month
        p_peak_vrijednosti.append(max(D__tm[start:end]))

    # fiksne vrijednosti
    """K_e = 100.0
    K_p = 200.0
    L_years = 10
    R_ir = 0.08"""

    # Cost per hour (same every day)
    C_e_tm = []
    for t in range(T_hours):
        if 7 <= t < 22:
            C_e_tm.append(VT)
        else:
            C_e_tm.append(NT)

    delta_t = 1.0
    eta_ch = 0.9
    eta_dis = 0.9
    SOC__min = 0.15
    SOC__max = 0.95
    P_distr = max(p_peak_vrijednosti)

    # Pravljenje modela
    model = ConcreteModel()
    model.M = RangeSet(0, months - 1)
    model.T = RangeSet(0, T_per_month - 1)

    def D_init(model, t, mm):
        idx = t + mm * T_per_month
        return D__tm[idx]

    def C_e_init(model, t):
        return C_e_tm[t % T_hours]

    # Parametri
    model.D = Param(model.T, model.M, initialize=D_init, within=pyo.NonNegativeReals)
    model.C_e = Param(model.T, initialize=C_e_init)
    model.C_p = Param(initialize=C_p)
    """model.K_e = Param(initialize=K_e)
    model.K_p = Param(initialize=K_p)
    model.L_years = Param(initialize=L_years)
    model.R_ir = Param(initialize=R_ir)"""
    model.delta_t = Param(initialize=delta_t)
    model.eta_ch = Param(initialize=eta_ch)
    model.eta_dis = Param(initialize=eta_dis)
    model.SOC_min = Param(initialize=SOC__min)
    model.SOC_max = Param(initialize=SOC__max)
    model.P_distr = Param(initialize=P_distr)
    model.e_bat = Param(initialize=velicina_battery)

    # Varijable; (12)
    model.p_bat = Var(domain=NonNegativeReals)
    model.p_ch = Var(model.T, model.M, domain=NonNegativeReals)
    model.p_dis = Var(model.T, model.M, domain=NonNegativeReals)
    model.s = Var(model.T, model.M, domain=NonNegativeReals)

    # p_peak_m
    def p_peak_values(model, mm):
        return (0.0, p_peak_vrijednosti[mm])
    model.p_peak = Var(model.M, domain=NonNegativeReals, bounds=p_peak_values)

    # Formule
    """def P1_rule(model):
        return (model.p_bat * model.K_p + model.e_bat * model.K_e) * (1.0 + model.R_ir) ** model.L_years / model.L_years
    model.P1 = Expression(rule=P1_rule)"""

    def P2_rule(model):
        return sum(
            model.C_e[t] * model.delta_t *
            (model.D[t, mm] + model.p_ch[t, mm] / model.eta_ch - model.p_dis[t, mm] * model.eta_dis)
            for mm in model.M for t in model.T)

    model.P2 = Expression(rule=P2_rule)

    def P3_rule(model):
        return sum(model.C_p * model.p_peak[mm] for mm in model.M)

    model.P3 = Expression(rule=P3_rule)

    model.obj = Objective(expr=model.P2 + model.P3)

    # Constraints
    # (5)
    def form5(model, t, mm):
        return model.p_peak[mm] >= model.D[t, mm] + model.p_ch[t, mm] / model.eta_ch - model.p_dis[t, mm] * model.eta_dis
    model.constr5 = Constraint(model.T, model.M, rule=form5)

    # (6)
    def form6_1(model, t, mm):
        return model.s[t, mm] == model.s[t - 1, mm] + model.p_ch[t, mm] * model.delta_t - model.p_dis[t, mm] * model.delta_t
    model.constr6_1 = Constraint(model.T - {0}, model.M, rule=form6_1)

    def form6_2spoji(model, mm):
        last_t = T_per_month - 1
        return model.s[0, mm] == model.s[last_t, mm] + model.p_ch[0, mm] * model.delta_t - model.p_dis[0, mm] * model.delta_t
    model.constr6_2spoji = Constraint(model.M, rule=form6_2spoji)

    # (7)
    def form7_min(model, t, mm):
        return model.s[t, mm] >= model.SOC_min * model.e_bat
    model.constr7_min = Constraint(model.T, model.M, rule=form7_min)

    def form7_max(model, t, mm):
        return model.s[t, mm] <= model.SOC_max * model.e_bat
    model.constr7_max = Constraint(model.T, model.M, rule=form7_max)

    # (8)
    def form8(model, t, mm):
        return model.p_ch[t, mm] <= model.p_bat
    model.constr8 = Constraint(model.T, model.M, rule=form8)

    # (9)
    def form9(model, t, mm):
        return model.p_dis[t, mm] <= model.p_bat
    model.constr9 = Constraint(model.T, model.M, rule=form9)

    # (10)
    def form10(model, t, mm):
        return model.D[t, mm] - model.p_dis[t, mm] * model.eta_dis >= 0.0
    model.constr10 = Constraint(model.T, model.M, rule=form10)

    # (11)
    def form11(model, t, mm):
        return model.D[t, mm] + model.p_ch[t, mm] / model.eta_ch <= model.P_distr
    model.constr11 = Constraint(model.T, model.M, rule=form11)

    # Optimiziraj
    solver = SolverFactory("highs")
    solver.options["presolve"] = "on"
    solver.options["parallel"] = "off"
    solver.options["threads"] = 1

    result = solver.solve(model, tee=False)

    # sve ovo if e_bat > 0; scratch that
    # treba vratiti:
    # 1) originalna cijena, 2) nova cijena
    og_cijena = 0
    for i in range(0, 12*30*24):
        og_cijena += C_e_tm[i % 24] * D__tm[i]

    vrsna_cijena = 0
    for i in range(0, months):
        vrsna_cijena += C_p * p_peak_vrijednosti[i]
    og_cijena += vrsna_cijena
    # C_e_tm za originalnu potrošnju: C_e_tm*D__tm + vrsna_cijena
    # nova potrošnja: model.obj
    # ušteda: ukupno staro - ukupno novo
    # punjenje i praznjenje baterije kroz jedan dan u godini -> graf p_ch i p_dis

    usteda = og_cijena - value(model.obj)

    if str(result.solver.termination_condition).lower() == "optimal":
        p_ch_matrix = [[value(model.p_ch[t, mth]) for t in model.T] for mth in model.M]
        p_dis_matrix = [[value(model.p_dis[t, mth]) for t in model.T] for mth in model.M]
        return (round(value(model.obj), 2), round(og_cijena, 2),
                round(usteda, 2), p_ch_matrix, p_dis_matrix)
    else:
        return float("nan"), float("nan"), float("nan"), list[0]*(12*30*24), list[0]*(12*30*24)
