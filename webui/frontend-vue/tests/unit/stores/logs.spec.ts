import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useLogsStore } from '@/stores/logs';
import type { LogEntry } from '@/types';

describe('Logs Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  const createLogEntry = (
    level: LogEntry['level'],
    message: string
  ): LogEntry => ({
    timestamp: new Date().toISOString(),
    level,
    message,
  });

  describe('entries', () => {
    it('starts with empty entries', () => {
      const store = useLogsStore();
      expect(store.entries).toHaveLength(0);
    });

    it('adds entries', () => {
      const store = useLogsStore();
      const entry = createLogEntry('INFO', 'Test message');

      store.addEntry(entry);

      expect(store.entries).toHaveLength(1);
      expect(store.entries[0].message).toBe('Test message');
    });

    it('adds multiple entries', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('INFO', 'Message 1'),
        createLogEntry('WARNING', 'Message 2'),
      ]);

      expect(store.entries).toHaveLength(2);
    });

    it('clears entries', () => {
      const store = useLogsStore();
      store.addEntry(createLogEntry('INFO', 'Test'));

      store.clearEntries();

      expect(store.entries).toHaveLength(0);
    });

    it('trims old entries when exceeding max', () => {
      const store = useLogsStore();
      store.setMaxEntries(3);

      store.addEntries([
        createLogEntry('INFO', 'Entry 1'),
        createLogEntry('INFO', 'Entry 2'),
        createLogEntry('INFO', 'Entry 3'),
        createLogEntry('INFO', 'Entry 4'),
      ]);

      expect(store.entries).toHaveLength(3);
      expect(store.entries[0].message).toBe('Entry 2');
    });
  });

  describe('filtering', () => {
    it('filters by level', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('DEBUG', 'Debug message'),
        createLogEntry('INFO', 'Info message'),
        createLogEntry('WARNING', 'Warning message'),
        createLogEntry('ERROR', 'Error message'),
      ]);

      store.setFilterLevel('WARNING');

      expect(store.filteredEntries).toHaveLength(2);
      expect(store.filteredEntries[0].level).toBe('WARNING');
      expect(store.filteredEntries[1].level).toBe('ERROR');
    });

    it('filters by search query', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('INFO', 'Processing movies'),
        createLogEntry('INFO', 'Processing TV shows'),
        createLogEntry('INFO', 'Finished'),
      ]);

      store.setSearchQuery('movies');

      expect(store.filteredEntries).toHaveLength(1);
      expect(store.filteredEntries[0].message).toContain('movies');
    });

    it('combines filters', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('DEBUG', 'Debug processing'),
        createLogEntry('INFO', 'Info processing'),
        createLogEntry('WARNING', 'Warning processing'),
        createLogEntry('ERROR', 'Error message'),
      ]);

      store.setFilterLevel('WARNING');
      store.setSearchQuery('processing');

      expect(store.filteredEntries).toHaveLength(1);
      expect(store.filteredEntries[0].level).toBe('WARNING');
    });
  });

  describe('computed properties', () => {
    it('counts entries correctly', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('INFO', 'Message 1'),
        createLogEntry('INFO', 'Message 2'),
      ]);

      expect(store.entryCount).toBe(2);
    });

    it('counts errors', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('INFO', 'Info'),
        createLogEntry('ERROR', 'Error 1'),
        createLogEntry('ERROR', 'Error 2'),
        createLogEntry('CRITICAL', 'Critical'),
      ]);

      expect(store.errorCount).toBe(3);
      expect(store.hasErrors).toBe(true);
    });

    it('counts warnings', () => {
      const store = useLogsStore();

      store.addEntries([
        createLogEntry('INFO', 'Info'),
        createLogEntry('WARNING', 'Warning 1'),
        createLogEntry('WARNING', 'Warning 2'),
      ]);

      expect(store.warningCount).toBe(2);
      expect(store.hasWarnings).toBe(true);
    });
  });

  describe('connection state', () => {
    it('tracks connection state', () => {
      const store = useLogsStore();

      expect(store.connected).toBe(false);

      store.setConnected(true);

      expect(store.connected).toBe(true);
      expect(store.connecting).toBe(false);
    });

    it('tracks connecting state', () => {
      const store = useLogsStore();

      store.setConnecting(true);

      expect(store.connecting).toBe(true);
    });
  });

  describe('auto-scroll', () => {
    it('defaults to enabled', () => {
      const store = useLogsStore();
      expect(store.autoScroll).toBe(true);
    });

    it('can be toggled', () => {
      const store = useLogsStore();

      store.toggleAutoScroll();

      expect(store.autoScroll).toBe(false);
    });
  });

  describe('reset', () => {
    it('resets all state', () => {
      const store = useLogsStore();

      store.addEntry(createLogEntry('INFO', 'Test'));
      store.setConnected(true);
      store.setFilterLevel('ERROR');
      store.setSearchQuery('test');

      store.reset();

      expect(store.entries).toHaveLength(0);
      expect(store.connected).toBe(false);
      expect(store.filterLevel).toBe('ALL');
      expect(store.searchQuery).toBe('');
    });
  });
});
