DELIMITER //
CREATE PROCEDURE sp_nova_reserva(
    IN p_id_usuario INT, 
    IN p_id_equipamento INT, 
    IN p_inicio DATETIME, 
    IN p_fim DATETIME
)
BEGIN
    DECLARE conflito INT DEFAULT 0;

    -- Verifica se já existe reserva que sobreponha o horário pedido
    SELECT COUNT(*) INTO conflito
    FROM Reserva
    WHERE id_equipamento = p_id_equipamento
    AND (
        (p_inicio >= inicio AND p_inicio < fim) OR
        (p_fim > inicio AND p_fim <= fim) OR
        (p_inicio <= inicio AND p_fim >= fim)
    );

    IF conflito > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: Conflito de horário. Já existe reserva neste período.';
    ELSE
        INSERT INTO Reserva (id_usuario, id_equipamento, inicio, fim)
        VALUES (p_id_usuario, p_id_equipamento, p_inicio, p_fim);
    END IF;
END;
//
DELIMITER ;