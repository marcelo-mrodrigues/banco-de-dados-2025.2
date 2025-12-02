CREATE OR REPLACE VIEW vw_agenda_reservas AS
SELECT 
    r.id_reserva,
    u.nome_completo AS usuario,
    e.nome_equipamento,
    p.nome AS parque,
    r.inicio,
    r.fim,
    e.status_conservacao
FROM Reserva r
JOIN Usuario u ON r.id_usuario = u.id_usuario
JOIN Equipamento e ON r.id_equipamento = e.id_equipamento
JOIN Parque p ON e.id_parque = p.id_parque;