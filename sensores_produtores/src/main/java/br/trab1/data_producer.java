package br.com.trab1;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;
import java.util.Date;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Classe dos Sensores, componente do "mini-mundo" simulados por Docker containers
 *  que geram dados periodicos (temperatura, vibração, consumo de energia, etc.) e
 * enviam mensagens para um topico kafka (dados-sensores).
 */
public class data_producer{

    public data_producer(){}

    public static void main(String[] args){
        //TODO : gerar dados periodicos em um JSON e enviar para o tópico kafka

        data_producer producer = new data_producer();


    }
}

/* Exemplo do copilot pra gerar dados em JSON

// ...existing code...
import com.google.gson.Gson;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class data_producer {

    public data_producer() {}

    public static void main(String[] args) {
        Gson gson = new Gson();
        String filePath = "sensor_data.json";

        for (int i = 0; i < 10; i++) { // Generates 10 samples
            Map<String, Object> sensorData = new HashMap<>();
            sensorData.put("timestamp", new Date().toString());
            sensorData.put("temperatura", 20 + Math.random() * 10); // 20-30°C
            sensorData.put("vibracao", Math.random() * 5); // 0-5 units
            sensorData.put("consumo_energia", 100 + Math.random() * 50); // 100-150W

            String json = gson.toJson(sensorData);

            try (FileWriter writer = new FileWriter(filePath, true)) {
                writer.write(json + "\n");
            } catch (IOException e) {
                e.printStackTrace();
            }

            try {
                Thread.sleep(1000); // Wait 1 second
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
// ...existing code... */