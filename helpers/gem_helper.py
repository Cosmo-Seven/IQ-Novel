# helpers/gem_helper.py

def calculate_gem_usage(user, price: int) -> dict:
    if price == 0:
        return {"free_gems_used": 0, "paid_gems_used": 0, "can_afford": True}

    if user.free_gem >= price:
        return {"free_gems_used": price, "paid_gems_used": 0, "can_afford": True}

    if user.gem >= price:
        return {"free_gems_used": 0, "paid_gems_used": price, "can_afford": True}

    return {"free_gems_used": 0, "paid_gems_used": 0, "can_afford": False}


def deduct_gems(user, free_gems_used: int, paid_gems_used: int):
    user.free_gem = max(0, user.free_gem - free_gems_used)
    user.gem      = max(0, user.gem - paid_gems_used)
    user.save(update_fields=["free_gem", "gem"])