# i = 0
# t0: i8 = const[1];
# t1: bool = eq(t9, t0);
# t2: bool = and(t1, en);
# t3: i8 = mux(t2, t0, t9);

# i = 1
# t4: i8 = const[0];
# t5: bool = eq(t9, t4);
# t6: bool = and(t5, en);
# t7: i8 = mux(t6, t4, t3);

# t8: bool = or(t2, t6)

# t9: i8 = reg[0](t7, t8)

#     t1: i8 = const[1];
#     t4: bool = eq(t2, t1);
#     t6: bool = and(t4, done);
#     t8: i8 = mux(t5, t1, t7);
#     t9: bool = or(t5, t6);
#     state: i8 = id(t2);
# }


def name(ident, num):
    return "{}{}".format(ident, num)


def expr(ident, ty):
    return "{}:{}".format(ident, ty)


def binop(dst, op, lhs, rhs):
    return "{} = {}({}, {});".format(dst, op, lhs, rhs)


def ins_mux(dst, cond, tru, fal):
    return "{} = mux({}, {}, {});".format(dst, cond, tru, fal)


def ins_id(dst, inp):
    return "{} = id({});".format(dst, inp)


def ins_reg(dst, lhs, rhs):
    return binop(dst, "reg[0]", lhs, rhs)


def ins_eq(dst, lhs, rhs):
    return binop(dst, "eq", lhs, rhs)


def ins_or(dst, lhs, rhs):
    return binop(dst, "or", lhs, rhs)


def ins_and(dst, lhs, rhs):
    return binop(dst, "and", lhs, rhs)


def ins_const(dst, value):
    return "{} = const[{}];".format(dst, value)


def fsm(en, y, size):
    assert size >= 2
    ty = "i8"
    tmp = "t"
    body = []
    t = 0
    reg_in_name = name(tmp, size * 6 - 1)
    reg_en_name = name(tmp, size * 6 - 2)
    cur = [i for i in range(size)]
    nxt = [i + 1 if i != size - 1 else 0 for i in range(size)]
    red = []
    for (c, n) in zip(cur, nxt):
        body.append(ins_const(expr(name(tmp, t), ty), c))
        body.append(ins_const(expr(name(tmp, t + 1), ty), n))
        body.append(
            ins_eq(expr(name(tmp, t + 2), "bool"), reg_in_name, name(tmp, t))
        )
        body.append(
            ins_and(expr(name(tmp, t + 3), "bool"), en, name(tmp, t + 2))
        )
        red.append(name(tmp, t + 3))
        if c == 0:
            body.append(
                ins_mux(
                    expr(name(tmp, t + 4), ty),
                    name(tmp, t + 3),
                    name(tmp, t + 1),
                    reg_in_name,
                )
            )
        else:
            body.append(
                ins_mux(
                    expr(name(tmp, t + 4), ty),
                    name(tmp, t + 3),
                    name(tmp, t + 1),
                    name(tmp, t - 1),
                )
            )
        t += 5
    for i in range(size - 1):
        if i == 0:
            body.append(ins_or(expr(name(tmp, t), "bool"), red[0], red[1]))
        else:
            body.append(
                ins_or(expr(name(tmp, t), "bool"), name(tmp, t - 1), red[i + 1])
            )
        t += 1
    body.append(
        ins_reg(expr(name(tmp, t), ty), name(tmp, t - size), reg_en_name)
    )
    body.append(ins_id(expr(y, ty), name(tmp, t)))
    return body


def sig(name, en, y, ty):
    inp = expr(en, "bool")
    out = expr(y, ty)
    sig = "def {}({})->({})".format(name, inp, out)
    return sig


def prog(sig, body):
    body = "\n".join(body)
    prog = "{} {{\n{}\n}}".format(sig, body)
    return prog


def emit(name, size):
    ty = "i8"
    en = "en"
    y = "y"
    s = sig(name, en, y, ty)
    body = fsm(en, y, size)
    return prog(s, body)


if __name__ == "__main__":
    print(emit("fsm", 8))