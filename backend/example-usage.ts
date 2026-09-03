/**
 * Ejemplo de Uso del Sistema Autónomo Controlado
 * 
 * Este archivo muestra cómo utilizar el sistema autónomo de forma segura
 */

import { AutonomousAPI } from './index';

async function demonstrateAutonomousSystem() {
  console.log('=== Sistema Autónomo Controlado - Demostración ===\n');

  // 1. Iniciar el sistema con un controlador humano
  console.log('1. Iniciando sistema...');
  await AutonomousAPI.start('human-controller-001');
  console.log('✓ Sistema iniciado\n');

  // 2. Verificar estado inicial
  console.log('2. Estado del sistema:');
  const status = AutonomousAPI.getStatus();
  console.log(JSON.stringify(status, null, 2));
  console.log();

  // 3. Procesar solicitud de baja urgencia
  console.log('3. Procesando solicitud de baja urgencia...');
  const lowUrgencyRequest = {
    type: 'generate_plan',
    data: { goal: 'Lanzar curso en 30 días' },
    urgency: 'low' as const
  };
  
  const result1 = await AutonomousAPI.processRequest(lowUrgencyRequest);
  console.log('Resultado:', JSON.stringify(result1, null, 2));
  console.log();

  // 4. Procesar solicitud de alta urgencia
  console.log('4. Procesando solicitud de alta urgencia...');
  const highUrgencyRequest = {
    type: 'optimize_tasks',
    data: { projectId: '123' },
    urgency: 'high' as const
  };
  
  const result2 = await AutonomousAPI.processRequest(highUrgencyRequest);
  console.log('Resultado:', JSON.stringify(result2, null, 2));
  console.log();

  // 5. Verificar estado después de acciones
  console.log('5. Estado actual del sistema:');
  const updatedStatus = AutonomousAPI.getStatus();
  console.log(JSON.stringify(updatedStatus, null, 2));
  console.log();

  // 6. Aprobar acción pendiente (si la hay)
  if (result2.requiresHumanApproval) {
    console.log('6. Aprobando acción pendiente...');
    try {
      await AutonomousAPI.approveAction('action-123', 'human-controller-001');
      console.log('✓ Acción aprobada\n');
    } catch (error) {
      console.log('✗ Error al aprobar:', error);
    }
  }

  // 7. Simular acción que requiere aprobación
  console.log('7. Simulando acción de alto riesgo...');
  const riskyRequest = {
    type: 'delete_user_data',
    data: { userId: 'user-123' },
    urgency: 'medium' as const
  };
  
  const result3 = await AutonomousAPI.processRequest(riskyRequest);
  console.log('Resultado:', JSON.stringify(result3, null, 2));
  console.log();

  // 8. Detener el sistema
  console.log('8. Deteniendo sistema...');
  await AutonomousAPI.stop('human-controller-001');
  console.log('✓ Sistema detenido\n');

  console.log('=== Demostración completada ===');
}

/**
 * Ejemplo de integración con AutoPlan
 */
async function integrateWithAutoPlan() {
  console.log('=== Integración con AutoPlan ===\n');

  // Iniciar sistema
  await AutonomousAPI.start('autoplan-admin');

  // Solicitar generación de plan autónoma
  const planRequest = {
    type: 'generate_plan',
    data: {
      goal: 'Quiero aprender React en 2 semanas',
      preferences: {
        intensity: 'medium',
        focus: 'practical'
      }
    },
    urgency: 'low' as const
  };

  const result = await AutonomousAPI.processRequest(planRequest);

  if (result.success) {
    console.log('✓ Plan generado autónomamente');
    console.log('Resultado:', result.result);
  } else if (result.requiresHumanApproval) {
    console.log('⚠ La acción requiere aprobación humana');
    console.log('Decisión:', result.decision);
    
    // Aquí el humano aprobaría o rechazaría
    // await AutonomousAPI.approveAction(actionId, 'autoplan-admin');
  } else {
    console.log('✗ Acción bloqueada por seguridad');
    console.log('Verificación de seguridad:', result.safetyCheck);
  }

  // Detener sistema
  await AutonomousAPI.stop('autoplan-admin');
}

/**
 * Ejemplo de monitoreo continuo
 */
async function continuousMonitoring() {
  console.log('=== Monitoreo Continuo ===\n');

  await AutonomousAPI.start('monitor-admin');

  // Simular monitoreo continuo
  const monitorInterval = setInterval(async () => {
    const status = AutonomousAPI.getStatus();
    
    console.log('--- Monitoreo ---');
    console.log('Activo:', status.isActive);
    console.log('Acciones del agente:', status.agentStatus.actionCount);
    console.log('Eventos de seguridad:', status.safetyStatus.criticalEventsCount);
    console.log('Tasa de aprobación humana:', status.decisionStats.humanApprovalRate.toFixed(1) + '%');
    
    // Si hay demasiados eventos críticos, detener
    if (status.safetyStatus.criticalEventsCount > 5) {
      console.log('⚠ Demasiados eventos críticos - deteniendo sistema');
      await AutonomousAPI.stop('monitor-admin');
      clearInterval(monitorInterval);
    }
  }, 5000); // Cada 5 segundos

  // Para demostración, detener después de 30 segundos
  setTimeout(async () => {
    clearInterval(monitorInterval);
    await AutonomousAPI.stop('monitor-admin');
    console.log('Monitoreo finalizado');
  }, 30000);
}

// Ejecutar demostración (comentar las que no se quieran ejecutar)
// demonstrateAutonomousSystem();
// integrateWithAutoPlan();
// continuousMonitoring();

export { demonstrateAutonomousSystem, integrateWithAutoPlan, continuousMonitoring };