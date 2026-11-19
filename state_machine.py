from database import get_db

def initialize_state_schema():
    from database import init_db
    init_db()

def transition_operation(op_id, new_status):
    with get_db() as conn:
        conn.execute('UPDATE operations SET status = ? WHERE id = ?', (new_status, op_id))
        conn.commit()
    return True
