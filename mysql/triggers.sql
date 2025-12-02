DELIMITER //
CREATE TRIGGER trg_verificar_status_antes_reserva
BEFORE INSERT ON Reserva
FOR EACH ROW
BEGIN
    DECLARE status_atual VARCHAR(50);
    
    SELECT status_conservacao INTO status_atual
    FROM Equipamento
    WHERE id_equipamento = NEW.id_equipamento;

    IF status_atual <> 'Funcional' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: Equipamento não está funcional e não pode ser reservado.';
    END IF;
END;
//
DELIMITER ;