// User state management
const userStates = new Map();

export const getUserState = (userId) => userStates.get(userId) || null;
export const setUserState = (userId, state) => userStates.set(userId, state);
export const resetUserState = (userId) => userStates.delete(userId);

// Helper functions untuk state management
export const hasUserState = (userId) => userStates.has(userId);
export const getAllActiveUsers = () => Array.from(userStates.keys());
export const getTotalActiveUsers = () => userStates.size;
export const clearAllStates = () => userStates.clear();

// State utilities
export const updateUserState = (userId, updates) => {
    const currentState = getUserState(userId) || {};
    const newState = { ...currentState, ...updates };
    setUserState(userId, newState);
    return newState;
};

export const getUserStateValue = (userId, key, defaultValue = null) => {
    const state = getUserState(userId);
    return state && state[key] !== undefined ? state[key] : defaultValue;
};
