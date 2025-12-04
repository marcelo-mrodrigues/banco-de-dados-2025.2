DELIMITER //
DROP TRIGGER IF EXISTS trg_verificar_status_equipamento; //
CREATE TRIGGER trg_verificar_status_equipamento
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

DELIMITER //
DROP TRIGGER IF EXISTS trg_verifica_disponibilidade_reserva; //
CREATE TRIGGER trg_verifica_disponibilidade_reserva
BEFORE UPDATE ON Reserva
FOR EACH ROW
BEGIN
    DECLARE conflitos INT DEFAULT 0;
    
    SELECT COUNT(*) INTO conflitos
    FROM Reserva
    WHERE id_equipamento = NEW.id_equipamento
      AND id_reserva <> OLD.id_reserva
      AND (
        NEW.inicio <= fim 
        AND
        NEW.fim >= inicio 
      );
      
    IF conflitos > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: Este equipamento já está reservado por outro usuário neste período.';
    END IF;
END;
//
DELIMITER ;
